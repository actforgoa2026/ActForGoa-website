import Foundation

struct SearchConfiguration: Decodable, Sendable {
    struct Intent: Decodable, Sendable { let pattern: String; let terms: [String]; let boost: [String] }
    struct Weights: Decodable, Sendable {
        let title, body, topic, expandedTitle, expandedBody, allTerms, exactPhrase, intentBoost, minimum, semanticThreshold, semanticOffset, semanticWeight: Double
    }
    let stopWords: String
    let intents: [Intent]
    let weights: Weights
}

struct SearchMatch: Sendable { let record: GuideRecord; var score: Double }

struct SearchEngine: Sendable {
    private struct Indexed: Sendable {
        let record: GuideRecord
        let title, body, topic: String
        let titleTokens, bodyTokens: Set<String>
    }
    let configuration: SearchConfiguration
    private let stop: Set<String>
    private let index: [Indexed]
    init(records: [GuideRecord], configuration: SearchConfiguration) {
        self.configuration = configuration
        let stop = Set(configuration.stopWords.split(separator: " ").map(String.init))
        self.stop = stop
        self.index = records.map { record in
            let title = record.title.lowercased(), body = (record.text + " " + (record.documentText ?? "")).lowercased()
            return Indexed(record: record, title: title, body: body, topic: record.topics.joined(separator: " ").lowercased(), titleTokens: Set(Self.tokens(title, stop: stop)), bodyTokens: Set(Self.tokens(body, stop: stop)))
        }
    }
    static func tokens(_ text: String, stop: Set<String>) -> [String] {
        text.lowercased().decomposedStringWithCompatibilityMapping
            .replacingOccurrences(of: #"[^a-z0-9\s]"#, with: " ", options: .regularExpression)
            .split(whereSeparator: \.isWhitespace).map(String.init).filter { $0.count > 1 && !stop.contains($0) }
    }
    func search(_ query: String, semantic: [String: Double]? = nil) -> [SearchMatch] {
        guard !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return index.map { .init(record: $0.record, score: 0) } }
        let terms = Self.tokens(query, stop: stop)
        let intents = configuration.intents.filter { query.range(of: $0.pattern, options: [.regularExpression, .caseInsensitive]) != nil }
        let expanded = Set(intents.flatMap(\.terms)).subtracting(terms)
        let weights = configuration.weights
        var matches: [SearchMatch] = []
        for item in index {
            var score = 0.0, hit = 0
            if !terms.isEmpty || !expanded.isEmpty {
                for term in terms {
                    if item.titleTokens.contains(term) || item.title.contains(term) { score += weights.title; hit += 1 }
                    else if item.bodyTokens.contains(term) { score += weights.body; hit += 1 }
                    else if item.topic.contains(term) { score += weights.topic }
                }
                for term in expanded.sorted() {
                    if item.title.contains(term) { score += weights.expandedTitle }
                    else if item.body.contains(term) { score += weights.expandedBody }
                }
                if !terms.isEmpty && hit == terms.count { score += weights.allTerms }
                if item.title.contains(query.lowercased()) { score += weights.exactPhrase }
                if intents.contains(where: { $0.boost.contains(item.record.id) }) { score += weights.intentBoost }
            }
            if score < weights.minimum { score = 0 }
            if let similarity = semantic?[item.record.id], similarity >= weights.semanticThreshold {
                score += (similarity - weights.semanticOffset) * weights.semanticWeight
            }
            if score > 0 { matches.append(.init(record: item.record, score: score)) }
        }
        return matches.sorted {
            if abs($0.score - $1.score) > 0.0000001 { return $0.score > $1.score }
            let order = $0.record.title.compare($1.record.title, options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "en_US"))
            return order == .orderedSame ? $0.record.id < $1.record.id : order == .orderedAscending
        }
    }
}
