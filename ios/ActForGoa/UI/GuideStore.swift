import SwiftUI

@MainActor @Observable final class GuideStore {
    private(set) var records: [GuideRecord] = []
    private(set) var practicalGuides: [PracticalGuide] = []
    private(set) var engine: SearchEngine?
    private(set) var error: String?
    private(set) var loading = false
    let contentURL: URL
    let semantic: SemanticSearch
    private var imageCache: [String: UIImage] = [:]
    init() {
        contentURL = Bundle.main.resourceURL!.appendingPathComponent("Content")
        semantic = SemanticSearch(root: contentURL)
    }
    func load() async {
        guard !loading else { return }
        loading = true; error = nil
        do {
            let root = contentURL
            let (records, guides, engine) = try await Task.detached(priority: .userInitiated) {
                let decoder = JSONDecoder()
                let archive = try decoder.decode([GuideRecord].self, from: Data(contentsOf: root.appendingPathComponent("data/catalog.json")))
                let guides = try decoder.decode([PracticalGuide].self, from: Data(contentsOf: root.appendingPathComponent("data/practical-guides.json")))
                let records = guides.filter(\.listed).map(\.record) + archive
                let config = try decoder.decode(SearchConfiguration.self, from: Data(contentsOf: root.appendingPathComponent("search-config.json")))
                return (records, guides, SearchEngine(records: records, configuration: config))
            }.value
            self.records = records; self.practicalGuides = guides; self.engine = engine
        } catch { self.error = "The saved field guide couldn’t open. Try again, or visit ActForGoa online." }
        loading = false
    }
    func image(_ path: String) -> UIImage? {
        guard path.hasPrefix("/assets/"), !path.contains("..") else { return nil }
        if let image = imageCache[path] { return image }
        guard let image = UIImage(contentsOfFile: contentURL.appendingPathComponent(String(path.dropFirst())).path) else { return nil }
        imageCache[path] = image
        return image
    }
    func record(_ id: String) -> GuideRecord? { records.first { $0.id == id } }
}

enum GuideRoute: Hashable { case record(String) }

struct RouteDestinations: ViewModifier {
    @Environment(GuideStore.self) private var store
    func body(content: Content) -> some View {
        content.navigationDestination(for: GuideRoute.self) { route in
            switch route {
            case .record(let id):
                if let guide = store.practicalGuides.first(where: { $0.id == id }) { PracticalGuideView(guide: guide) }
                else if let record = store.record(id) { RecordDetail(record: record) }
                else { ContentUnavailableView("Entry not found", systemImage: "book.closed", description: Text("This entry isn’t in the bundled guide. Search the collection or open its web link.")) }
            }
        }
    }
}
