import SwiftUI

struct RootView: View {
    @Environment(GuideStore.self) private var store
    @State private var selected = 0
    @State private var explorePath: [GuideRoute] = []
    var body: some View {
        Group {
            if let error = store.error {
                ContentUnavailableView {
                    Label("The guide couldn’t open", systemImage: "book.closed")
                } description: { Text(error) } actions: {
                    Button("Try again") { Task { await store.load() } }.buttonStyle(.borderedProminent)
                    Link("Visit ActForGoa", destination: URL(string: "https://actforgoa.org/")!)
                }
            } else if store.engine == nil {
                ProgressView("Opening your field guide…").frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                TabView(selection: $selected) {
                    Tab("Explore", systemImage: "magnifyingglass", value: 0) {
                        NavigationStack(path: $explorePath) { CatalogueView(mode: .explore).modifier(RouteDestinations()) }
                    }
                    Tab("Directory", systemImage: "person.2", value: 1) {
                        NavigationStack { CatalogueView(mode: .directory).modifier(RouteDestinations()) }
                    }
                    Tab("Library", systemImage: "books.vertical", value: 2) {
                        NavigationStack { CatalogueView(mode: .library).modifier(RouteDestinations()) }
                    }
                    Tab("Community", systemImage: "leaf", value: 3) {
                        NavigationStack { CommunityView().modifier(RouteDestinations()) }
                    }
                }
            }
        }
        .background(GuideTheme.paper)
        .onOpenURL { url in
            guard let id = Self.entryID(url) else { return }
            selected = 0; explorePath = [.record(id)]
        }
    }
    static func entryID(_ url: URL) -> String? {
        if url.scheme == "actforgoa", url.host == "read" { return url.pathComponents.dropFirst().first }
        guard url.host == "actforgoa-field-guide.vercel.app", url.pathComponents.count == 3, url.pathComponents[1] == "read" else { return nil }
        return url.pathComponents[2]
    }
}

enum CatalogueMode: String {
    case explore, directory, library, stories
    var title: String {
        switch self { case .explore: "ActForGoa"; case .directory: "Directory"; case .library: "Reading library"; case .stories: "Community stories" }
    }
    func includes(_ kind: RecordKind) -> Bool {
        switch self { case .explore: true; case .directory: kind == .organisation || kind == .contact; case .library: kind == .resource; case .stories: kind == .story }
    }
}

struct CatalogueView: View {
    let mode: CatalogueMode
    @Environment(GuideStore.self) private var store
    @Environment(\.dynamicTypeSize) private var typeSize
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var query = ""
    @State private var topic = ""
    @State private var kind = "all"
    @State private var grid = false
    @State private var showAll = false
    @State private var limit = 24
    @State private var matches: [SearchMatch] = []
    @State private var status = ""
    private var browsing: Bool { mode != .explore || showAll || !query.isEmpty || !topic.isEmpty || kind != "all" }
    private var filtered: [GuideRecord] {
        matches.map(\.record).filter { mode.includes($0.kind) && (topic.isEmpty || $0.topics.contains(topic)) && (kind == "all" || $0.kind.rawValue == kind || (kind == "organisation" && $0.kind == .contact)) }
    }
    private var grouped: Bool { mode == .explore && !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && kind == "all" }
    private var groups: [(String, [GuideRecord])] {
        let definitions: [(String, [RecordKind])] = [("People & organisations", [.organisation, .contact]), ("Guides & reading", [.resource]), ("Stories & projects", [.story]), ("About & action", [.page])]
        let records = filtered
        return definitions.map { name, kinds in (name, records.filter { kinds.contains($0.kind) }) }.filter { !$0.1.isEmpty }
            .sorted { a, b in records.firstIndex(of: a.1[0])! < records.firstIndex(of: b.1[0])! }
    }
    var body: some View {
        List {
            if !browsing { introduction }
            else {
                if query.isEmpty && topic.isEmpty && kind == "all" { catalogueIntroduction }
                if !topic.isEmpty || kind != "all" {
                    ViewThatFits(in: .horizontal) {
                        HStack { activeFilter; Spacer(); clearFilters }
                        VStack(alignment: .leading) { activeFilter; clearFilters }
                    }.catalogueRow()
                }
                VStack(alignment: .leading, spacing: 8) {
                    Text("\(filtered.count) \(filtered.count == 1 ? "result" : "results")").font(GuideTheme.heading).accessibilityIdentifier("result-count")
                    if !status.isEmpty { Text(status).font(.caption).foregroundStyle(GuideTheme.secondary).accessibilityIdentifier("search-status") }
                }.catalogueRow()
                if query.range(of: "snake|cobra", options: [.regularExpression, .caseInsensitive]) != nil {
                    SourceNotice(text: "These volunteer and wildlife contacts come from the original site. Confirm availability directly; the numbers have not been independently reverified.").catalogueRow()
                }
                if filtered.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        ContentUnavailableView.search(text: query)
                        Text("Try “waste”, “wildlife” or “panchayat”, or remove a filter.").foregroundStyle(GuideTheme.secondary)
                        Button("Browse all entries") { query = ""; topic = ""; kind = "all"; showAll = true }.buttonStyle(.borderedProminent).foregroundStyle(GuideTheme.onTint).controlSize(.large)
                    }.catalogueRow()
                } else if grouped {
                    ForEach(groups, id: \.0) { group in
                        Section {
                            rows(Array(group.1.prefix(max(6, limit / 4))))
                        } header: { Text("\(group.0) · \(group.1.count)").font(.headline).foregroundStyle(GuideTheme.ink) }
                    }
                    if groups.contains(where: { $0.1.count > max(6, limit / 4) }) { moreButton }
                } else {
                    Section { rows(Array(filtered.prefix(limit))) }
                    if filtered.count > limit { moreButton }
                }
            }
        }
        .listStyle(.plain).scrollContentBackground(.hidden).background(GuideTheme.paper).textCase(nil)
        .foregroundStyle(GuideTheme.ink).tint(GuideTheme.tint)
        .navigationTitle(mode.title)
        .navigationBarTitleDisplayMode(.inline)
        .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "What would you like help with?")
        .autocorrectionDisabled().textInputAutocapitalization(.never)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Picker("Topic", selection: $topic) {
                        Text("All topics").tag("")
                        ForEach(GuideTopics.all, id: \.self) { Text($0).tag($0) }
                    }
                    if mode == .explore {
                        Picker("Entry type", selection: $kind) {
                            Text("Everything").tag("all")
                            Text("People & organisations").tag("organisation")
                            Text("Guides & resources").tag("resource")
                            Text("Stories").tag("story")
                            Text("About & action").tag("page")
                        }
                    }
                    Toggle("Show images", isOn: $grid)
                } label: { Label("Filter entries", systemImage: topic.isEmpty && kind == "all" ? "line.3.horizontal.decrease" : "line.3.horizontal.decrease.circle.fill") }
                .accessibilityIdentifier("filters")
            }
        }
        .task(id: query) { await search() }
        .onChange(of: topic) { limit = 24 }
        .onChange(of: kind) { limit = 24 }
    }
    private var introduction: some View {
        Group {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .center, spacing: 16) {
                    Text("Enabling people to care for Goa.").font(GuideTheme.display).tracking(-0.7)
                        .fixedSize(horizontal: false, vertical: true).frame(maxWidth: .infinity, alignment: .leading)
                    if !typeSize.isAccessibilitySize {
                        LocalPhoto(path: "/assets/goa-river.webp", label: "Palms reflected in a Goan waterway")
                            .frame(width: 100, height: 142).clipped().clipShape(RoundedRectangle(cornerRadius: 24))
                    }
                }
                Text("Good people. Local knowledge. Practical ways to help.").font(.subheadline).foregroundStyle(GuideTheme.secondary)
            }.padding(.vertical, 6).catalogueRow()
            VStack(alignment: .leading, spacing: 6) {
                Text("Find practical help").font(.subheadline.weight(.semibold)).padding(.bottom, 4)
                ForEach(Array(["Snake rescue", "Waste & recycling", "Composting at home"].enumerated()), id: \.element) { index, starter in
                    if index > 0 { Divider().overlay(GuideTheme.ink.opacity(0.1)) }
                    Button { query = starter } label: {
                        HStack(spacing: 12) {
                            Text(starter).font(.headline).multilineTextAlignment(.leading)
                            Spacer(minLength: 4)
                            Image(systemName: "arrow.up.right").font(.body.weight(.medium)).accessibilityHidden(true)
                        }.frame(minHeight: 44).contentShape(Rectangle())
                    }.buttonStyle(.plain).accessibilityLabel(starter)
                }
            }.padding(20).background(GuideTheme.citrus, in: RoundedRectangle(cornerRadius: 24)).catalogueRow()
            VStack(alignment: .leading, spacing: 16) {
                SectionHeading(title: "What do you care about?")
                LazyVGrid(columns: topicColumns, spacing: 12) {
                    ForEach(GuideTopics.all, id: \.self) { name in
                        Button { topic = name } label: {
                            VStack(alignment: .leading, spacing: 20) {
                                Image(systemName: GuideTheme.topicSymbol(name)).font(.title2.weight(.medium)).accessibilityHidden(true)
                                Text(name).font(.headline).multilineTextAlignment(.leading).fixedSize(horizontal: false, vertical: true)
                            }.frame(maxWidth: .infinity, minHeight: 100, alignment: .leading).padding(16)
                                .background(GuideTheme.topicColor(name), in: RoundedRectangle(cornerRadius: 20))
                        }.buttonStyle(.plain).accessibilityIdentifier("topic-\(name)")
                    }
                }
                Button { showAll = true } label: {
                    HStack { Text("Browse all \(store.records.count) entries"); Spacer(); Image(systemName: "arrow.right") }.frame(minHeight: 44)
                }.font(.headline)
            }.padding(.top, 12).catalogueRow()
            Section {
                ForEach(["guide-farming", "guide-animal-welfare", "guide-environmental-protection"], id: \.self) { id in
                    if let record = store.record(id) { RecordRow(record: record, showImage: false).catalogueRow() }
                }
            } header: { SectionHeading(title: "Useful guides").padding(.vertical, 8) }
            VStack(alignment: .leading, spacing: 12) {
                Text("For the Goa we love.").font(GuideTheme.heading)
                Text("Saved on your phone. Every entry links to its original source.").font(.subheadline).foregroundStyle(GuideTheme.secondary)
            }.padding(.vertical, 12).catalogueRow()
        }
    }
    private var topicColumns: [GridItem] { Array(repeating: GridItem(.flexible(), spacing: 12, alignment: .top), count: typeSize.isAccessibilitySize ? 1 : 2) }
    private var activeFilter: some View { TopicLabel(topic: topic.isEmpty ? (RecordKind(rawValue: kind)?.label ?? "All entries") : topic) }
    private var clearFilters: some View { Button("Clear filters") { topic = ""; kind = "all" }.foregroundStyle(GuideTheme.tint).frame(minHeight: 44) }
    private var catalogueIntroduction: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(mode == .directory ? "Good people.\nLocal connections." : mode == .library ? "Local knowledge.\nPractical next steps." : "Small acts.\nA shared future.")
                .font(GuideTheme.display).fixedSize(horizontal: false, vertical: true)
            Text(mode == .directory ? "Find organisations and volunteer contacts. Confirm listed details before you go." : mode == .library ? "Guides, resources and reading from the ActForGoa collection." : "Meet the people and projects caring for Goa.")
                .font(.subheadline).foregroundStyle(GuideTheme.secondary)
        }.frame(maxWidth: .infinity, alignment: .leading).padding(22)
            .background(mode == .directory ? GuideTheme.lilac : mode == .library ? GuideTheme.aqua : GuideTheme.coral, in: RoundedRectangle(cornerRadius: 24))
            .catalogueRow()
    }
    @ViewBuilder private func rows(_ records: [GuideRecord]) -> some View {
        if grid && !typeSize.isAccessibilitySize {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 280), spacing: 20)], spacing: 24) {
                ForEach(records) { record in RecordRow(record: record, showImage: true) }
            }.padding(.vertical, 8).catalogueRow()
        } else {
            ForEach(records) { record in RecordRow(record: record, showImage: false).catalogueRow() }
        }
    }
    private var moreButton: some View { Button("Show more results") { limit += 24 }.buttonStyle(.bordered).controlSize(.large).frame(maxWidth: .infinity, minHeight: 44).catalogueRow() }
    private func search() async {
        guard let engine = store.engine else { return }
        limit = 24
        matches = engine.search(query)
        guard !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { status = ""; return }
        status = "Keyword results ready. Matching meaning on your phone…"
        do {
            try await Task.sleep(for: .milliseconds(250))
            let scores = try await store.semantic.scores(for: query)
            try Task.checkCancellation()
            withAnimation(reduceMotion ? nil : .easeOut(duration: 0.2)) { matches = engine.search(query, semantic: scores) }
            status = "Matched by meaning and keywords, on your phone."
        } catch is CancellationError { return }
        catch { if !Task.isCancelled { status = "Keyword search is available. Meaning search couldn’t load." } }
    }
}

struct RecordRow: View {
    let record: GuideRecord
    let showImage: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            NavigationLink(value: GuideRoute.record(record.id)) {
                VStack(alignment: .leading, spacing: 10) {
                    if showImage && !record.image.isEmpty {
                        LocalPhoto(path: record.image).frame(height: 190).clipped().clipShape(RoundedRectangle(cornerRadius: 18))
                    }
                    Text(record.title).font(.system(.title3, design: .rounded, weight: .bold)).foregroundStyle(GuideTheme.ink)
                        .fixedSize(horizontal: false, vertical: true).frame(maxWidth: .infinity, alignment: .leading)
                    Label((record.editorialStatus == "authored-practical-guide" ? "Practical guide · Draft" : record.kind.label) + (record.locality.map { " · \($0)" } ?? ""), systemImage: record.kind.symbol)
                        .font(.caption.weight(.medium)).foregroundStyle(GuideTheme.secondary)
                    Text(record.displaySummary).font(.subheadline).foregroundStyle(GuideTheme.secondary).lineLimit(3)
                }
            }.buttonStyle(.plain).accessibilityIdentifier("record-\(record.id)")
            if record.kind == .contact || record.kind == .organisation, let phone = record.phones.first(where: { $0.url != nil }) ?? record.phones.first {
                VStack(alignment: .leading, spacing: 2) {
                    if let url = phone.url { Link(destination: url) { Label(phone.display, systemImage: "phone").frame(minHeight: 44) }.foregroundStyle(GuideTheme.tint).buttonStyle(.borderless) }
                    else { Text(phone.display).font(.subheadline) }
                    Text(record.kind == .contact ? "Source list: 2018 · please confirm details" : "Listed contact · please confirm details").font(.caption).foregroundStyle(GuideTheme.secondary)
                }
            }
            Divider().padding(.top, 8)
        }.padding(.top, 8)
    }
}
