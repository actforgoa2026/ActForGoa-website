import SwiftUI
import SafariServices

struct BrowserDestination: Identifiable { let url: URL; var id: String { url.absoluteString } }
struct BrowserSheet: UIViewControllerRepresentable {
    let url: URL
    func makeUIViewController(context: Context) -> SFSafariViewController { SFSafariViewController(url: url) }
    func updateUIViewController(_ controller: SFSafariViewController, context: Context) {}
}

struct RecordDetail: View {
    let record: GuideRecord
    @Environment(GuideStore.self) private var store
    @State private var browser: BrowserDestination?
    @State private var correction = false
    private var related: [GuideRecord] {
        Array(store.records.filter { $0.id != record.id && $0.kind == record.kind && !$0.topics.filter(record.topics.contains).isEmpty }.prefix(3))
    }
    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 24) {
                VStack(alignment: .leading, spacing: 12) {
                    Text(record.title).font(GuideTheme.display).foregroundStyle(GuideTheme.ink)
                        .accessibilityAddTraits(.isHeader)
                    if let topic = record.topics.first { TopicLabel(topic: topic) }
                    Text(record.kind.label).font(.subheadline.weight(.medium)).foregroundStyle(GuideTheme.secondary)
                    Text("From ActForGoa" + (record.publishedAt.isEmpty ? "" : " · Published \(GuideRecord.dateLabel(record.publishedAt))")).font(.subheadline).foregroundStyle(GuideTheme.secondary)
                }
                if !record.image.isEmpty {
                    LocalPhoto(path: record.image, label: record.title).frame(height: 230).clipped().clipShape(RoundedRectangle(cornerRadius: 22))
                }
                if !record.phones.isEmpty || record.kind == .organisation {
                    SourceNotice(text: "This is an archived source listing. Contact details and service availability need confirmation. Retrieved \(GuideRecord.dateLabel(record.retrievedAt)).")
                }
                if (record.kind == .contact || record.kind == .organisation) && hasContacts {
                    contactSection
                }
                ForEach(Array(record.blocks.enumerated()), id: \.offset) { _, block in
                    if block.type == "heading" {
                        Text(block.text).font(GuideTheme.heading).padding(.top, 12).accessibilityAddTraits(.isHeader)
                    } else {
                        Text(block.text).font(.body).lineSpacing(5).textSelection(.enabled)
                    }
                }
                if record.kind != .contact && record.kind != .organisation && hasContacts { contactSection }
                if !record.documents.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        sectionTitle("Documents & downloads")
                        ForEach(Array(record.documents.enumerated()), id: \.offset) { _, document in
                            VStack(alignment: .leading, spacing: 4) {
                                webButton(document.label, url: document.url, symbol: "doc.text")
                                if let pages = document.pages { Text("\(pages) pages").font(.caption).foregroundStyle(GuideTheme.secondary) }
                                if let status = document.status, status >= 400 {
                                    Text("The original link returned \(status); it may be unavailable.").font(.subheadline).foregroundStyle(GuideTheme.secondary)
                                }
                            }
                        }
                    }
                }
                let links = record.links.filter { SafeLink.web($0.url) != nil }
                if !links.isEmpty {
                    DisclosureGroup("Links from the original entry (\(links.count))") {
                        VStack(alignment: .leading, spacing: 12) {
                            ForEach(Array(links.enumerated()), id: \.offset) { _, link in webButton(link.label, url: link.url) }
                        }.padding(.top, 12)
                    }
                }
                Divider()
                VStack(alignment: .leading, spacing: 12) {
                    sectionTitle("Keep the source close.")
                    Text("Retrieved \(GuideRecord.dateLabel(record.retrievedAt)). Contact information is source-listed and unverified.").font(.subheadline).foregroundStyle(GuideTheme.secondary)
                    webButton("Original ActForGoa page", url: record.source)
                    if !record.sourceApi.isEmpty { webButton("Public directory record", url: record.sourceApi) }
                    if let status = record.sourceStatus, status >= 400 { Text("The source returned \(status) when archived.").font(.subheadline).foregroundStyle(GuideTheme.secondary) }
                    ShareLink(item: record.shareURL) { Label("Share this entry", systemImage: "square.and.arrow.up").frame(minHeight: 44) }
                    Button { correction = true } label: { Label("Suggest a correction", systemImage: "square.and.pencil").frame(minHeight: 44) }
                }
                if !related.isEmpty {
                    Divider()
                    sectionTitle("Keep exploring")
                    ForEach(related) { RecordRow(record: $0, showImage: false) }
                }
            }.padding(20).readingWidth()
        }
        .background(GuideTheme.paper).foregroundStyle(GuideTheme.ink)
        .navigationTitle(record.kind == .contact || record.kind == .organisation ? "Directory entry" : "Reading")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar { ShareLink(item: record.shareURL) { Label("Share entry", systemImage: "square.and.arrow.up") } }
        .sheet(item: $browser) { BrowserSheet(url: $0.url).ignoresSafeArea() }
        .sheet(isPresented: $correction) { ContactView(entry: record.title) }
    }
    private var hasContacts: Bool { !record.phones.isEmpty || !record.emails.isEmpty || !record.locations.isEmpty }
    private var contactSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            sectionTitle("Get in touch")
            ForEach(Array(record.phones.prefix(5).enumerated()), id: \.offset) { _, phone in
                if let url = phone.url {
                    Link(destination: url) { Label(phone.display, systemImage: "phone").frame(minHeight: 44) }
                } else { Label(phone.display, systemImage: "phone").textSelection(.enabled) }
            }
            if record.phones.count > 5 {
                DisclosureGroup("More published numbers (\(record.phones.count - 5))") {
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(Array(record.phones.dropFirst(5).enumerated()), id: \.offset) { _, phone in
                            if let url = phone.url { Link(destination: url) { Label(phone.display, systemImage: "phone").frame(minHeight: 44) } }
                            else { Text(phone.display).textSelection(.enabled) }
                        }
                    }
                }
            }
            ForEach(record.emails, id: \.self) { email in
                if let url = SafeLink.email(email) { Link(destination: url) { Label(email, systemImage: "envelope").frame(minHeight: 44) } }
            }
            ForEach(record.locations, id: \.self) { Label($0, systemImage: "mappin.and.ellipse") }
            Text("Published contact information, not a confirmation of current availability. Read the original entry for full context.").font(.subheadline).foregroundStyle(GuideTheme.secondary)
        }
    }
    private func sectionTitle(_ title: String) -> some View { SectionHeading(title: title) }
    @ViewBuilder private func webButton(_ label: String, url: String, symbol: String = "arrow.up.right") -> some View {
        if let url = SafeLink.web(url) {
            Button { browser = .init(url: url) } label: {
                Label(label.isEmpty ? (url.host ?? "Open source") : label, systemImage: symbol).frame(minHeight: 44, alignment: .leading).multilineTextAlignment(.leading)
            }
        }
    }
}
