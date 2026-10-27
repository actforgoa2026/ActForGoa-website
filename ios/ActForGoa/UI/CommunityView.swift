import SwiftUI

struct CommunityView: View {
    @Environment(GuideStore.self) private var store
    @State private var contact = false
    @State private var volunteer = false
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 28) {
                VStack(alignment: .leading, spacing: 0) {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("A better Goa starts with us.").font(GuideTheme.display).fixedSize(horizontal: false, vertical: true)
                        Text("Your time, your knowledge, your little corner of Goa. It all matters.").font(.body)
                    }.padding(22).frame(maxWidth: .infinity, alignment: .leading).background(GuideTheme.coral)
                    LocalPhoto(path: "/assets/candolim-cleanup.webp", label: "Volunteers at the Candolim beach cleanup")
                        .frame(height: 200).clipped()
                }.clipShape(RoundedRectangle(cornerRadius: 26))
                VStack(alignment: .leading, spacing: 16) {
                    SectionHeading(title: "Take your next step")
                    Button { volunteer = true } label: {
                        HStack { Text("Get involved"); Spacer(); Image(systemName: "arrow.right") }.font(.headline).frame(minHeight: 44)
                    }.buttonStyle(.borderedProminent).foregroundStyle(GuideTheme.onTint).controlSize(.large)
                    communityAction("Contact ActForGoa", symbol: "envelope") { contact = true }
                    Link(destination: URL(string: "https://actforgoa.org/volunteer/")!) { actionLabel("Give your time", symbol: "heart") }
                    Link(destination: URL(string: "https://actforgoa.org/greenviksitgoa/")!) { actionLabel("Shape Goa’s future", symbol: "leaf") }
                }
                VStack(alignment: .leading, spacing: 16) {
                    SectionHeading(title: "Small acts. A shared future.")
                    if let story = store.record("wp-9352") { RecordRow(record: story, showImage: true) }
                    NavigationLink { CatalogueView(mode: .stories) } label: { actionLabel("All community stories", symbol: "text.book.closed") }
                }
                VStack(alignment: .leading, spacing: 12) {
                    NavigationLink { AboutView() } label: { actionLabel("About ActForGoa", symbol: "info.circle") }
                    Link("Privacy policy", destination: URL(string: "https://actforgoa.org/privacy-policy/")!).frame(minHeight: 44)
                    Link("Terms & conditions", destination: URL(string: "https://actforgoa.org/terms-and-conditions/")!).frame(minHeight: 44)
                    Text("Kokum Trust is the legal managing entity for Act for Goa.").font(.footnote).foregroundStyle(GuideTheme.secondary)
                }
            }.padding(20).readingWidth()
        }.background(GuideTheme.paper).foregroundStyle(GuideTheme.ink).navigationTitle("Community").navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $contact) { ContactView() }
            .sheet(isPresented: $volunteer) { ContactView(involve: true) }
    }
    private func communityAction(_ title: String, symbol: String, action: @escaping () -> Void) -> some View {
        Button(action: action) { actionLabel(title, symbol: symbol) }
    }
    private func actionLabel(_ title: String, symbol: String) -> some View {
        HStack(spacing: 12) {
            Label(title, systemImage: symbol).multilineTextAlignment(.leading)
            Spacer(minLength: 4)
            Image(systemName: "arrow.up.right").font(.caption.weight(.semibold)).accessibilityHidden(true)
        }.font(.headline).foregroundStyle(GuideTheme.tint).frame(minHeight: 44).padding(.vertical, 2).contentShape(Rectangle())
    }
}

struct AboutView: View {
    @Environment(GuideStore.self) private var store
    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 22) {
                Text("A platform for everyone who loves Goa.").font(GuideTheme.display).accessibilityAddTraits(.isHeader)
                Text("Enabling people to care for Goa.").font(.title3)
                Text("Why ActForGoa exists").font(.title2.weight(.semibold)).accessibilityAddTraits(.isHeader)
                Text("ACTforGOA is a new platform to help sustainable development take root in Goa.")
                Text("What future could be possible if we all worked together to keep Goa Clean and Green now and for the future?")
                if let about = store.record("wp-2059") {
                    Text("In ActForGoa’s own words").font(.title2.weight(.semibold)).accessibilityAddTraits(.isHeader)
                    ForEach(Array(about.blocks.filter { $0.text.count > 75 && !$0.text.contains("ACTforGOA is a new platform") }.enumerated()), id: \.offset) { _, block in Text(block.text).lineSpacing(5) }
                }
                Link("Read the original About page", destination: URL(string: "https://actforgoa.org/about-2/")!).frame(minHeight: 44)
                Link("Annual reports", destination: URL(string: "https://actforgoa.org/about-2/annual-reports/")!).frame(minHeight: 44)
                Link("Press coverage", destination: URL(string: "https://actforgoa.org/press-coverage/")!).frame(minHeight: 44)
                Divider()
                Text("About this field guide").font(.title2.weight(.semibold)).accessibilityAddTraits(.isHeader)
                Text("This development preview bundles original ActForGoa entries and five practical guides with official sources, templates and visible verification flags. The practical guides remain drafts for legal and service review. Some original records are historical; contact details have not been independently verified.")
                Text("Search combines keywords with the same MiniLM language model used by the web field guide. It runs on your phone, finds existing entries and does not generate advice. No account is needed, and your searches are not sent to an AI provider.")
                Text("The catalogue and search work offline. Source websites, documents, calls and email need the appropriate connection or app. Content updates arrive with a new app build.")
                Text("Contact forms prepare an email for you to review and send. The guide does not store submissions. The original ActForGoa website remains the source.")
                Text("Model: all-MiniLM-L6-v2, Apache 2.0. Runtime: ONNX Runtime, MIT. Original content and photography remain attributable to their owners.").font(.footnote).foregroundStyle(GuideTheme.secondary)
                NavigationLink("Model licence and attribution") { LicenceView() }.frame(minHeight: 44)
            }.padding(20).readingWidth().textSelection(.enabled)
        }.background(GuideTheme.paper).foregroundStyle(GuideTheme.ink).navigationTitle("About").navigationBarTitleDisplayMode(.inline)
    }
}

struct LicenceView: View {
    @Environment(GuideStore.self) private var store
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                ForEach(["models/all-MiniLM-L6-v2/NOTICE", "models/all-MiniLM-L6-v2/LICENSE", "onnxruntime-LICENSE"], id: \.self) { path in
                    Text((try? String(contentsOf: store.contentURL.appendingPathComponent(path), encoding: .utf8)) ?? "Licence unavailable in this build.").font(.body).textSelection(.enabled)
                }
            }.padding(20).readingWidth()
        }.background(GuideTheme.paper).navigationTitle("Licences").navigationBarTitleDisplayMode(.inline)
    }
}
