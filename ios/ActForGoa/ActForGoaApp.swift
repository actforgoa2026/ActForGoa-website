import SwiftUI

@main struct ActForGoaApp: App {
    @State private var store = GuideStore()
    var body: some Scene {
        WindowGroup {
            RootView().environment(store).tint(GuideTheme.tint)
                .task { await store.load() }
        }
    }
}
