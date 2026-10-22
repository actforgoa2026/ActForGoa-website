import Foundation

enum RecordKind: String, Codable, CaseIterable, Sendable {
    case organisation, contact, resource, story, page
    var label: String {
        switch self {
        case .organisation: "Organisation"
        case .contact: "Volunteer contact"
        case .resource: "Guide & resource"
        case .story: "Community story"
        case .page: "ActForGoa"
        }
    }
    var symbol: String {
        switch self {
        case .organisation, .contact: "person.2"
        case .resource: "book"
        case .story: "leaf"
        case .page: "doc.text"
        }
    }
}

struct GuideRecord: Codable, Identifiable, Hashable, Sendable {
    struct Block: Codable, Hashable, Sendable { let type: String; let text: String }
    struct Phone: Codable, Hashable, Sendable {
        let display: String; let href: String?; let verification: String
        var url: URL? {
            guard let href, href.range(of: #"^tel:\+91\d{10}$"#, options: .regularExpression) != nil else { return nil }
            return URL(string: href)
        }
    }
    struct Document: Codable, Hashable, Sendable { let label: String; let url: String; let status: Int?; let pages: Int? }
    struct SourceLink: Codable, Hashable, Sendable { let label: String; let url: String }
    let id: String
    let title: String
    let kind: RecordKind
    let source: String
    let sourceApi: String
    let sourceStatus: Int?
    let summary: String
    let text: String
    let documentText: String?
    let blocks: [Block]
    let topics: [String]
    let image: String
    let imageSource: String
    let publishedAt: String
    let updatedAt: String
    let retrievedAt: String
    let phones: [Phone]
    let emails: [String]
    let locations: [String]
    let locality: String?
    let documents: [Document]
    let links: [SourceLink]
    let verification: String
    let editorialStatus: String
    var shareURL: URL { URL(string: "https://actforgoa-field-guide.vercel.app/read/\(id)")! }
    var displaySummary: String {
        id == "resource-590480849c" ? "A locality-by-locality list of snake rescue volunteers, published in 2018. Contact details need current confirmation." : summary
    }
    static func dateLabel(_ raw: String) -> String {
        guard !raw.isEmpty else { return "Date not provided" }
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let date = iso.date(from: raw) ?? ISO8601DateFormatter().date(from: raw)
        if let date { return date.formatted(.dateTime.day().month(.wide).year().locale(Locale(identifier: "en_GB"))) }
        // WordPress dates can lack an offset; preserve their calendar day.
        let datePart = String(raw.prefix(10))
        let f = DateFormatter(); f.locale = Locale(identifier: "en_US_POSIX"); f.dateFormat = "yyyy-MM-dd"
        if let date = f.date(from: datePart) { return date.formatted(.dateTime.day().month(.wide).year().locale(Locale(identifier: "en_GB"))) }
        return raw
    }
}

enum GuideTopics {
    static let all = ["Waste & recycling", "Nature & wildlife", "Water & environment", "Community & rights", "Food & farming", "Culture & heritage", "Planning & mobility", "Health & wellbeing"]
    static let symbols = ["arrow.3.trianglepath", "leaf", "water.waves", "person.2", "carrot", "building.columns", "figure.walk", "heart"]
}

enum SafeLink {
    static func web(_ value: String) -> URL? {
        guard let url = URL(string: value), ["https", "http"].contains(url.scheme?.lowercased() ?? ""), url.host != nil else { return nil }
        return url
    }
    static func email(_ address: String) -> URL? {
        guard !address.contains("\n"), !address.contains("\r"), address.contains("@") else { return nil }
        var c = URLComponents(); c.scheme = "mailto"; c.path = address
        return c.url
    }
}

struct EmailDraft: Equatable, Sendable {
    var name = ""
    var email = ""
    var reason = "Ask a question"
    var message = ""
    var entry = ""
    var valid: Bool {
        !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        email.range(of: #"^[^\s@]+@[^\s@]+\.[^\s@]+$"#, options: .regularExpression) != nil &&
        !message.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && name.count <= 100 && email.count <= 160 && message.count <= 4000
    }
    var body: String { "\(message)\n\nName: \(name)\nReply to: \(email)" + (entry.isEmpty ? "" : "\nEntry: \(entry)") }
    var mailURL: URL? {
        var c = URLComponents(); c.scheme = "mailto"; c.path = "info@actforgoa.org"
        c.queryItems = [.init(name: "subject", value: reason), .init(name: "body", value: body)]
        return c.url
    }
}
