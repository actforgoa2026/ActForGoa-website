import Foundation

struct PracticalGuide: Decodable, Identifiable, Sendable {
    struct Template: Decodable, Hashable, Sendable { let label: String; let url: String }
    let id: String
    let title: String
    let heading: String
    let summary: String
    let topics: [String]
    let markdown: String
    let download: String
    let templates: [Template]
    let listed: Bool
    var record: GuideRecord {
        GuideRecord(id: id, title: title, kind: .resource, source: "/read/guide-sources", sourceApi: "", sourceStatus: nil,
                    summary: summary, text: markdown, documentText: nil, blocks: [], topics: topics, image: "", imageSource: "",
                    publishedAt: "", updatedAt: "2026-10-22", retrievedAt: "2026-10-22", phones: [], emails: [], locations: [], locality: nil,
                    documents: templates.map { .init(label: $0.label, url: $0.url, status: nil, pages: nil) }, links: [],
                    verification: "draft-review-required", editorialStatus: "authored-practical-guide")
    }
}

/// The published guide corpus uses headings, paragraphs, lists and GFM tables.
/// Retains all text and resolves reference-style citations before native rendering.
struct GuideMarkdown: Sendable {
    struct Block: Identifiable, Sendable {
        enum Kind: Sendable { case heading(Int), paragraph, listItem(String), table, code, divider }
        let id: Int
        let kind: Kind
        let text: String
        var headers: [String] = []
        var rows: [[String]] = []
    }
    let blocks: [Block]
    init(_ markdown: String, omitDraftPreamble: Bool = false) {
        let lines = markdown.components(separatedBy: .newlines)
        let definition = try! NSRegularExpression(pattern: #"^\[([^\]]+)\]:\s+(\S+)"#)
        var references: [String: String] = [:]
        var content: [String] = []
        for line in lines {
            let ns = line as NSString
            if let match = definition.firstMatch(in: line, range: NSRange(location: 0, length: ns.length)) {
                references[ns.substring(with: match.range(at: 1)).lowercased()] = ns.substring(with: match.range(at: 2))
            } else { content.append(line) }
        }
        let citation = try! NSRegularExpression(pattern: #"\[([^\]]+)\]\[([^\]]+)\]"#)
        func resolve(_ text: String) -> String {
            var result = text
            for match in citation.matches(in: text, range: NSRange(text.startIndex..., in: text)).reversed() {
                let ns = text as NSString
                guard let url = references[ns.substring(with: match.range(at: 2)).lowercased()], let range = Range(match.range, in: result) else { continue }
                result.replaceSubrange(range, with: "[\(ns.substring(with: match.range(at: 1)))](\(url))")
            }
            return result
        }
        func cells(_ line: String) -> [String] {
            var value = line.trimmingCharacters(in: .whitespaces)
            if value.hasPrefix("|") { value.removeFirst() }; if value.hasSuffix("|") { value.removeLast() }
            return value.components(separatedBy: "|").map { resolve($0.trimmingCharacters(in: .whitespaces)) }
        }
        var parsed: [Block] = [], paragraph: [String] = [], i = 0
        func append(_ kind: Block.Kind, _ text: String, headers: [String] = [], rows: [[String]] = []) {
            parsed.append(.init(id: parsed.count, kind: kind, text: resolve(text), headers: headers, rows: rows))
        }
        func flush() {
            if !paragraph.isEmpty { append(.paragraph, paragraph.joined(separator: "\n")); paragraph = [] }
        }
        while i < content.count {
            let line = content[i], trimmed = line.trimmingCharacters(in: .whitespaces)
            if trimmed.isEmpty { flush(); i += 1; continue }
            if omitDraftPreamble && parsed.isEmpty && paragraph.isEmpty && trimmed.hasPrefix("**Draft") { i += 1; continue }
            if trimmed.hasPrefix("```") {
                flush(); i += 1; var code: [String] = []
                while i < content.count && !content[i].hasPrefix("```") { code.append(content[i]); i += 1 }
                append(.code, code.joined(separator: "\n")); i += 1; continue
            }
            if trimmed == "---" { flush(); append(.divider, ""); i += 1; continue }
            if trimmed.hasPrefix("#"), let space = trimmed.firstIndex(of: " "), trimmed[..<space].allSatisfy({ $0 == "#" }) {
                flush(); append(.heading(trimmed.distance(from: trimmed.startIndex, to: space)), String(trimmed[trimmed.index(after: space)...])); i += 1; continue
            }
            if trimmed.hasPrefix("|"), i + 1 < content.count, content[i + 1].range(of: #"^\|?[\s:|\-]+\|?$"#, options: .regularExpression) != nil {
                flush(); let headers = cells(line); i += 2; var rows: [[String]] = []
                while i < content.count && content[i].trimmingCharacters(in: .whitespaces).hasPrefix("|") { rows.append(cells(content[i])); i += 1 }
                append(.table, "", headers: headers, rows: rows); continue
            }
            if let range = trimmed.range(of: #"^(?:[-*] |\d+\. )"#, options: .regularExpression) {
                flush(); let prefix = String(trimmed[range]); append(.listItem(prefix.first?.isNumber == true ? prefix : "• "), String(trimmed[range.upperBound...])); i += 1; continue
            }
            paragraph.append(line); i += 1
        }
        flush(); blocks = parsed
    }
}
