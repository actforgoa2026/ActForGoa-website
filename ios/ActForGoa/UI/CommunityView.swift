import SwiftUI

struct CommunityView: View {
    @Environment(GuideStore.self) private var store
    @State private var contact = false
    @State private var volunteer = false
    var body: some View {
        List {
            Section {
                Text("A better Goa starts with us.").font(.title2.weight(.semibold)).foregroundStyle(GuideTheme.ink)
                Text("Your time, your knowledge, your little corner of Goa. It all matters.").foregroundStyle(GuideTheme.secondary)
            }
            GuideSection("Take your next step") {
                Button { volunteer = true } label: { Label("Get involved", systemImage: "hands.sparkles") }
                Link(destination: URL(string: "https://actforgoa.org/volunteer/")!) { Label("Give your time", systemImage: "heart") }
                Link(destination: URL(string: "https://actforgoa.org/greenviksitgoa/")!) { Label("Shape Goa’s future", systemImage: "leaf") }
                Button { contact = true } label: { Label("Contact ActForGoa", systemImage: "envelope") }
            }
            GuideSection("Small acts. A shared future.") {
                if let story = store.record("wp-9352") { RecordRow(record: story, showImage: true) }
                NavigationLink { CatalogueView(mode: .stories) } label: { Label("All community stories", systemImage: "text.book.closed") }
            }
            Section {
                NavigationLink { AboutView() } label: { Label("About ActForGoa", systemImage: "info.circle") }
                Link("Privacy policy", destination: URL(string: "https://actforgoa.org/privacy-policy/")!)
                Link("Terms & conditions", destination: URL(string: "https://actforgoa.org/terms-and-conditions/")!)
            } footer: { Text("Kokum Trust is the legal managing entity for Act for Goa.") }
        }.guideList().textCase(nil).navigationTitle("Community")
            .sheet(isPresented: $contact) { ContactView() }
            .sheet(isPresented: $volunteer) { ContactView(involve: true) }
    }
}

struct AboutView: View {
    @Environment(GuideStore.self) private var store
    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 22) {
                Text("A platform for everyone who loves Goa.").font(.largeTitle.weight(.semibold)).accessibilityAddTraits(.isHeader)
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
