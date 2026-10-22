import SwiftUI

struct PracticalGuideView: View {
    let guide: PracticalGuide
    @Environment(GuideStore.self) private var store
    @State private var path: [String] = []
    @State private var document: LocalGuideFile?
    @State private var browser: BrowserDestination?
    @State private var correction = false
    private var parsed: GuideMarkdown { GuideMarkdown(guide.markdown, omitDraftPreamble: guide.listed) }
    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 24) {
                    Text(guide.heading).font(.largeTitle.weight(.semibold)).accessibilityAddTraits(.isHeader)
                    if !guide.summary.isEmpty { Text(guide.summary).font(.title3).foregroundStyle(GuideTheme.secondary) }
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Draft for review").font(.headline)
                        Text("Sources checked 22 October 2026. Legal review and live service checks remain open.").foregroundStyle(GuideTheme.secondary)
                        NavigationLink("See what needs verification", value: GuideRoute.record("guide-verification"))
                    }
                    DisclosureGroup("On this page") {
                        VStack(alignment: .leading, spacing: 8) {
                            ForEach(parsed.blocks) { block in
                                if case .heading(2) = block.kind {
                                    Button { proxy.scrollTo(block.id, anchor: .top) } label: { Text(block.text).multilineTextAlignment(.leading).frame(minHeight: 44) }
                                }
                            }
                        }.padding(.top, 8)
                    }
                    if !guide.templates.isEmpty {
                        DisclosureGroup("Templates to use (\(guide.templates.count))") {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Download, edit and use the required official form where one applies.").foregroundStyle(GuideTheme.secondary)
                                ForEach(guide.templates, id: \.url) { item in
                                    Button { document = .init(path: item.url, title: item.label) } label: { Label(item.label, systemImage: "doc.text").multilineTextAlignment(.leading).frame(minHeight: 44) }
                                }
                            }.padding(.top, 12)
                        }.accessibilityIdentifier("guide-templates")
                    }
                    ForEach(parsed.blocks) { block in
                        MarkdownBlockView(block: block).id(block.id)
                    }
                    Divider()
                    Text("Sources and review").font(.title2.weight(.semibold)).accessibilityAddTraits(.isHeader)
                    NavigationLink("Official source register", value: GuideRoute.record("guide-sources")).frame(minHeight: 44)
                    NavigationLink("Verification register", value: GuideRoute.record("guide-verification")).frame(minHeight: 44)
                    Button { document = .init(path: guide.download, title: guide.title) } label: { Label("Save or share this guide", systemImage: "square.and.arrow.up").frame(minHeight: 44) }
                    Button("Suggest a correction") { correction = true }.frame(minHeight: 44)
                    Text("Related practical guides").font(.title2.weight(.semibold)).accessibilityAddTraits(.isHeader)
                    ForEach(store.practicalGuides.filter { $0.listed && $0.id != guide.id }) { other in
                        NavigationLink(other.title, value: GuideRoute.record(other.id)).frame(minHeight: 44)
                    }
                }.padding(20).readingWidth()
            }
            .environment(\.openURL, OpenURLAction { url in
                if url.path.hasPrefix("/read/"), url.host == nil || url.host == "actforgoa-field-guide.vercel.app" {
                    path.append(String(url.path.dropFirst(6))); return .handled
                }
                if url.path.hasPrefix("/guides/"), url.host == nil || url.host == "actforgoa-field-guide.vercel.app" {
                    document = .init(path: url.path, title: url.lastPathComponent); return .handled
                }
                if let safe = SafeLink.web(url.absoluteString) { browser = .init(url: safe); return .handled }
                return .discarded
            })
        }
        .background(GuideTheme.paper).foregroundStyle(GuideTheme.ink).tint(GuideTheme.tint)
        .navigationTitle("Practical guide").navigationBarTitleDisplayMode(.inline)
        .toolbar { ShareLink(item: guide.record.shareURL) { Label("Share guide", systemImage: "square.and.arrow.up") } }
        .navigationDestination(isPresented: Binding(get: { !path.isEmpty }, set: { if !$0 { path = [] } })) {
            if let id = path.last, let linked = store.practicalGuides.first(where: { $0.id == id }) { PracticalGuideView(guide: linked) }
        }
        .sheet(item: $document) { LocalGuideFileView(file: $0) }
        .sheet(item: $browser) { BrowserSheet(url: $0.url).ignoresSafeArea() }
        .sheet(isPresented: $correction) { ContactView(entry: guide.title) }
    }
}

struct MarkdownBlockView: View {
    let block: GuideMarkdown.Block
    var body: some View {
        switch block.kind {
        case .heading(let level):
            InlineGuideText(block.text).font(level <= 2 ? .title2.weight(.semibold) : .title3.weight(.semibold)).padding(.top, 12).accessibilityAddTraits(.isHeader)
        case .paragraph:
            InlineGuideText(block.text).lineSpacing(5)
        case .listItem(let prefix):
            HStack(alignment: .firstTextBaseline, spacing: 8) { Text(prefix); InlineGuideText(block.text).lineSpacing(4) }.accessibilityElement(children: .combine)
        case .table:
            VStack(alignment: .leading, spacing: 20) {
                ForEach(Array(block.rows.enumerated()), id: \.offset) { index, row in
                    if index > 0 { Divider() }
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(Array(row.enumerated()), id: \.offset) { column, cell in
                            VStack(alignment: .leading, spacing: 4) {
                                if column < block.headers.count { InlineGuideText(block.headers[column]).font(.caption.weight(.semibold)).foregroundStyle(GuideTheme.secondary) }
                                InlineGuideText(cell).font(column == 0 ? .headline : .body).lineSpacing(4)
                            }
                        }
                    }
                }
            }
        case .code:
            Text(block.text).font(.body.monospaced()).textSelection(.enabled)
        case .divider: Divider()
        }
    }
}

struct InlineGuideText: View {
    let text: String
    init(_ text: String) { self.text = text }
    var body: some View { Text(Self.attributed(text)).textSelection(.enabled).fixedSize(horizontal: false, vertical: true) }
    private static func attributed(_ text: String) -> AttributedString {
        var result = (try? AttributedString(markdown: text, options: .init(interpretedSyntax: .inlineOnlyPreservingWhitespace))) ?? AttributedString(text)
        // Preserve strong emphasis and links; all published type remains upright.
        for run in result.runs {
            if var intent = run.inlinePresentationIntent, intent.contains(.emphasized) {
                intent.remove(.emphasized); result[run.range].inlinePresentationIntent = intent
            }
        }
        return result
    }
}

struct LocalGuideFile: Identifiable {
    let path: String
    let title: String
    var id: String { path }
}

struct LocalGuideFileView: View {
    let file: LocalGuideFile
    @Environment(GuideStore.self) private var store
    @Environment(\.dismiss) private var dismiss
    private var url: URL? {
        guard file.path.hasPrefix("/guides/"), !file.path.contains("..") else { return nil }
        return store.contentURL.appendingPathComponent(String(file.path.dropFirst()))
    }
    var body: some View {
        NavigationStack {
            Group {
                if let url, let text = try? String(contentsOf: url, encoding: .utf8) {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 20) {
                            Text("Save a copy to edit").font(.title2.weight(.semibold))
                            Text("Use the required official form where one applies. Sharing opens a review sheet; nothing is sent automatically.").foregroundStyle(GuideTheme.secondary)
                            ShareLink(item: url) { Label("Save or share file", systemImage: "square.and.arrow.up").frame(minHeight: 44) }.accessibilityIdentifier("share-guide-file")
                            Divider()
                            Text(text).font(.body).textSelection(.enabled)
                        }.padding(20).readingWidth()
                    }
                } else {
                    ContentUnavailableView("File unavailable", systemImage: "doc", description: Text("This file is missing from the saved guide. Try a new app build."))
                }
            }
            .background(GuideTheme.paper).foregroundStyle(GuideTheme.ink)
            .navigationTitle(file.title).navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Done") { dismiss() } } }
        }.tint(GuideTheme.tint)
    }
}
