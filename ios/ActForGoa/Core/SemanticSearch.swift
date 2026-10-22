import Foundation
import OnnxRuntimeBindings

/// BERT WordPiece preprocessing used by the bundled all-MiniLM-L6-v2 tokenizer.
struct WordPieceTokenizer {
    private struct File: Decodable {
        struct Model: Decodable { let vocab: [String: Int64] }
        let model: Model
    }
    let vocabulary: [String: Int64]
    init(url: URL) throws { vocabulary = try JSONDecoder().decode(File.self, from: Data(contentsOf: url)).model.vocab }
    func encode(_ text: String) -> [Int64] {
        var cleaned = ""
        for scalar in text.unicodeScalars {
            let n = scalar.value
            if n == 0 || n == 0xFFFD { continue }
            if CharacterSet.whitespacesAndNewlines.contains(scalar) { cleaned += " "; continue }
            if CharacterSet.controlCharacters.contains(scalar) { continue }
            let chinese = (0x4E00...0x9FFF).contains(n) || (0x3400...0x4DBF).contains(n) || (0x20000...0x2FA1F).contains(n) || (0xF900...0xFAFF).contains(n)
            cleaned += chinese ? " \(scalar) " : String(scalar)
        }
        let normalized = cleaned.lowercased().decomposedStringWithCanonicalMapping.unicodeScalars.filter { !CharacterSet.nonBaseCharacters.contains($0) }
        var separated = ""
        for s in normalized {
            let n = s.value
            let punctuation = CharacterSet.punctuationCharacters.contains(s) || (33...47).contains(n) || (58...64).contains(n) || (91...96).contains(n) || (123...126).contains(n)
            separated += punctuation ? " \(s) " : String(s)
        }
        var ids: [Int64] = [101]
        for word in separated.split(whereSeparator: \.isWhitespace) {
            let chars = Array(word)
            if chars.count > 100 { ids.append(100); continue }
            var position = 0, pieces: [Int64] = []
            while position < chars.count {
                var end = chars.count
                var found: Int64?
                while end > position {
                    let piece = (position == 0 ? "" : "##") + String(chars[position..<end])
                    if let id = vocabulary[piece] { found = id; break }
                    end -= 1
                }
                guard let found else { pieces = [100]; break }
                pieces.append(found); position = end
            }
            ids.append(contentsOf: pieces)
        }
        // Transformers.js uses tokenizer_config.model_max_length (512).
        return Array(ids.prefix(511)) + [102]
    }
}

actor SemanticSearch {
    struct Index: Decodable { let dimensions: Int; let ids: [String]; let records: Int }
    enum Failure: Error { case invalidIndex, invalidOutput }
    private let root: URL
    private var environment: ORTEnv?
    private var session: ORTSession?
    private var tokenizer: WordPieceTokenizer?
    private var index: Index?
    private var vectors: [Float] = []
    init(root: URL) { self.root = root }
    private func prepare() throws {
        if session != nil { return }
        let model = root.appendingPathComponent("models/all-MiniLM-L6-v2")
        let index = try JSONDecoder().decode(Index.self, from: Data(contentsOf: root.appendingPathComponent("data/vector-index.json")))
        let bytes = try Data(contentsOf: root.appendingPathComponent("data/vectors.bin"))
        guard index.dimensions == 384, bytes.count == index.ids.count * 384 * 4 else { throw Failure.invalidIndex }
        let vectors = bytes.withUnsafeBytes { Array($0.bindMemory(to: Float.self)) }
        let tokenizer = try WordPieceTokenizer(url: model.appendingPathComponent("tokenizer.json"))
        let environment = try ORTEnv(loggingLevel: .warning)
        let options = try ORTSessionOptions()
        try options.setIntraOpNumThreads(2)
        try options.setGraphOptimizationLevel(.all)
        let session = try ORTSession(env: environment, modelPath: model.appendingPathComponent("onnx/model_quantized.onnx").path, sessionOptions: options)
        self.environment = environment; self.session = session
        self.tokenizer = tokenizer; self.index = index; self.vectors = vectors
    }
    func embedding(_ query: String) throws -> [Float] {
        try prepare()
        guard let tokenizer, let session else { throw Failure.invalidOutput }
        let ids = tokenizer.encode(query)
        func tensor(_ values: [Int64]) throws -> ORTValue {
            let data = values.withUnsafeBufferPointer { Data(buffer: $0) }
            return try ORTValue(tensorData: NSMutableData(data: data), elementType: .int64, shape: [1, NSNumber(value: ids.count)])
        }
        let output = try session.run(withInputs: [
            "input_ids": tensor(ids), "attention_mask": tensor(Array(repeating: 1, count: ids.count)),
            "token_type_ids": tensor(Array(repeating: 0, count: ids.count))
        ], outputNames: ["last_hidden_state"], runOptions: nil)
        guard let value = output["last_hidden_state"] else { throw Failure.invalidOutput }
        let data = try value.tensorData() as Data
        guard data.count == ids.count * 384 * 4 else { throw Failure.invalidOutput }
        let values = data.withUnsafeBytes { Array($0.bindMemory(to: Float.self)) }
        var pooled = [Float](repeating: 0, count: 384)
        for token in ids.indices { for j in 0..<384 { pooled[j] += values[token * 384 + j] / Float(ids.count) } }
        let norm = sqrt(pooled.reduce(Float(0)) { $0 + $1 * $1 })
        guard norm > 0 else { throw Failure.invalidOutput }
        return pooled.map { $0 / norm }
    }
    func scores(for query: String) throws -> [String: Double] {
        let vector = try embedding(query)
        guard let index else { throw Failure.invalidIndex }
        var scores: [String: Double] = [:]
        for (i, id) in index.ids.enumerated() {
            var dot: Double = 0
            for j in 0..<384 { dot += Double(vector[j]) * Double(vectors[i * 384 + j]) }
            if dot > (scores[id] ?? 0) { scores[id] = dot }
        }
        return scores
    }
}
