import XCTest
@testable import ActForGoaCore

final class CoreTests: XCTestCase {
    static let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    struct Fixture: Decodable {
        struct Match: Decodable { let id: String; let score: Double }
        let query: String; let tokenIDs: [Int64]; let top: [Match]; let embedding: [Float]
    }
    func fixtures() throws -> [Fixture] { try JSONDecoder().decode([Fixture].self, from: Data(contentsOf: Bundle.module.url(forResource: "search-fixtures", withExtension: "json")!)) }
    func records() throws -> [GuideRecord] { try JSONDecoder().decode([GuideRecord].self, from: Data(contentsOf: Self.root.appendingPathComponent("public/data/catalog.json"))) }
    func guides() throws -> [PracticalGuide] { try JSONDecoder().decode([PracticalGuide].self, from: Data(contentsOf: Self.root.appendingPathComponent("src/content/guides.json"))) }
    func engine() throws -> SearchEngine {
        let config = try JSONDecoder().decode(SearchConfiguration.self, from: Data(contentsOf: Self.root.appendingPathComponent("shared/search-config.json")))
        return try SearchEngine(records: guides().filter(\.listed).map(\.record) + records(), configuration: config)
    }
    func testWebLexicalParity() throws {
        let engine = try engine()
        for fixture in try fixtures() {
            let actual = engine.search(fixture.query)
            // Compare rankings by score; ties may differ with ICU versions.
            XCTAssertEqual(actual.prefix(10).map { $0.record.id }.sorted(), fixture.top.map(\.id).sorted(), fixture.query)
            for expected in fixture.top { XCTAssertEqual(actual.first { $0.record.id == expected.id }!.score, expected.score, accuracy: 0.000001, fixture.query) }
        }
    }
    func testWebTokenizerParity() throws {
        let tokenizer = try WordPieceTokenizer(url: Self.root.appendingPathComponent("public/models/all-MiniLM-L6-v2/tokenizer.json"))
        for fixture in try fixtures() { XCTAssertEqual(tokenizer.encode(fixture.query), fixture.tokenIDs, fixture.query) }
    }
    func testRealModelMatchesWebEmbeddings() async throws {
        let semantic = SemanticSearch(root: Self.root.appendingPathComponent("public"))
        for fixture in try fixtures() where !fixture.query.isEmpty {
            let actual = try await semantic.embedding(fixture.query)
            XCTAssertEqual(actual.count, 384)
            let cosine = zip(actual, fixture.embedding).reduce(Float(0)) { $0 + $1.0 * $1.1 }
            // Quantized ARM kernels differ slightly between native ORT 1.24 and web ORT.
            // Require near-identical direction as well as the real retrieval assertions below.
            XCTAssertGreaterThan(cosine, 0.995, fixture.query)
        }
    }
    func testRealSemanticRetrievalAndHybridRanking() async throws {
        let semantic = SemanticSearch(root: Self.root.appendingPathComponent("public"))
        let engine = try engine()
        let scores = try await semantic.scores(for: "discarded household materials")
        let results = engine.search("discarded household materials", semantic: scores)
        XCTAssertTrue(results.prefix(15).contains { $0.record.title == "V Recycle" })
        let snakeScores = try await semantic.scores(for: "Who do I call about a snake in my lawn?")
        XCTAssertEqual(engine.search("Who do I call about a snake in my lawn?", semantic: snakeScores).first?.record.id, "resource-590480849c")
    }
    func testProvenanceAndPhoneSafety() throws {
        let records = try records()
        struct Summary: Decodable { let records: Int }
        let summary = try JSONDecoder().decode(Summary.self, from: Data(contentsOf: Self.root.appendingPathComponent("public/data/summary.json")))
        XCTAssertGreaterThan(records.count, 0)
        XCTAssertEqual(records.count, summary.records)
        XCTAssertEqual(Set(records.map(\.id)).count, records.count)
        XCTAssertTrue(records.allSatisfy { SafeLink.web($0.source)?.host == "actforgoa.org" && !$0.retrievedAt.isEmpty })
        let short = records.flatMap(\.phones).filter { $0.display.count == 7 }
        XCTAssertFalse(short.isEmpty)
        XCTAssertTrue(short.allSatisfy { $0.url == nil })
        XCTAssertNil(SafeLink.web("javascript:alert(1)"))
        XCTAssertNil(SafeLink.web("file:///private/test"))
    }
    func testDraftValidationAndEscaping() throws {
        var draft = EmailDraft()
        XCTAssertFalse(draft.valid)
        draft.name = "A & B"; draft.email = "test@example.org"; draft.message = "Please correct + # ? & = café"; draft.entry = "Some entry"
        XCTAssertTrue(draft.valid)
        let c = URLComponents(url: try XCTUnwrap(draft.mailURL), resolvingAgainstBaseURL: false)!
        XCTAssertEqual(c.queryItems?.first { $0.name == "body" }?.value, draft.body)
        XCTAssertTrue(draft.body.contains("Entry: Some entry"))
        draft.message = String(repeating: "a", count: 4001); XCTAssertFalse(draft.valid)
    }
    func testPracticalGuideCorpusAndCitations() throws {
        let guides = try guides()
        XCTAssertEqual(guides.filter(\.listed).count, 5)
        for guide in guides {
            let parsed = GuideMarkdown(guide.markdown)
            XCTAssertFalse(parsed.blocks.isEmpty, guide.id)
            let rendered = parsed.blocks.map { $0.text + $0.headers.joined() + $0.rows.flatMap { $0 }.joined() }.joined()
            XCTAssertNil(rendered.range(of: #"\[[^\]]+\]\[[^\]]+\]"#, options: .regularExpression), guide.id)
            for file in [guide.download] + guide.templates.map(\.url) {
                XCTAssertTrue(FileManager.default.fileExists(atPath: Self.root.appendingPathComponent("public" + file).path), file)
            }
        }
    }
    func testMarkdownPreservesStructureAndResolvesReferences() {
        let markdown = "## A step\n\nRead [the source][S1].\n\n1. First\n- Next\n\n| Situation | Action |\n| --- | --- |\n| Garden | [Apply](/read/guide-farming) |\n\n[S1]: https://example.org/source"
        let blocks = GuideMarkdown(markdown).blocks
        XCTAssertEqual(blocks.count, 5)
        XCTAssertEqual(blocks[1].text, "Read [the source](https://example.org/source).")
        XCTAssertEqual(blocks[4].headers, ["Situation", "Action"])
        XCTAssertEqual(blocks[4].rows, [["Garden", "[Apply](/read/guide-farming)"]])
    }
    func testHistoricalDatePreserved() {
        XCTAssertEqual(GuideRecord.dateLabel("22 October 2018"), "22 October 2018")
        XCTAssertTrue(GuideRecord.dateLabel("2018-10-22T10:00:00").contains("2018"))
    }
}
