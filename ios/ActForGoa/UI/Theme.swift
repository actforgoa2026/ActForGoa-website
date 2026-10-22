import SwiftUI
import UIKit

enum GuideTheme {
    static let paper = Color(UIColor { $0.userInterfaceStyle == .dark ? UIColor(red: 0.065, green: 0.105, blue: 0.09, alpha: 1) : UIColor(red: 0.969, green: 0.969, blue: 0.933, alpha: 1) })
    static let ink = Color(UIColor { $0.userInterfaceStyle == .dark ? UIColor(red: 0.92, green: 0.95, blue: 0.90, alpha: 1) : UIColor(red: 0.125, green: 0.239, blue: 0.204, alpha: 1) })
    static let tint = Color(UIColor { $0.userInterfaceStyle == .dark ? UIColor(red: 0.66, green: 0.85, blue: 0.71, alpha: 1) : UIColor(red: 0.086, green: 0.247, blue: 0.212, alpha: 1) })
    static let secondary = Color(UIColor { $0.userInterfaceStyle == .dark ? UIColor(red: 0.67, green: 0.75, blue: 0.70, alpha: 1) : UIColor(red: 0.36, green: 0.42, blue: 0.39, alpha: 1) })
    static let surface = Color(UIColor.secondarySystemGroupedBackground)
}

struct LocalPhoto: View {
    let path: String
    var label: String = ""
    @Environment(GuideStore.self) private var store
    var body: some View {
        if let image = store.image(path) {
            Image(uiImage: image).resizable().scaledToFill()
                .accessibilityLabel(label).accessibilityHidden(label.isEmpty)
        }
    }
}

struct SourceNotice: View {
    let text: String
    var body: some View {
        Text(text).font(.subheadline).foregroundStyle(GuideTheme.secondary)
            .frame(maxWidth: .infinity, alignment: .leading).padding(16)
            .background(GuideTheme.surface, in: RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func guideList() -> some View {
        self.scrollContentBackground(.hidden).background(GuideTheme.paper)
            .listStyle(.insetGrouped).tint(GuideTheme.tint)
    }
    func readingWidth() -> some View { self.frame(maxWidth: 680, alignment: .leading).frame(maxWidth: .infinity) }
}

struct GuideSection<Content: View>: View {
    let title: String
    let content: Content
    init(_ title: String, @ViewBuilder content: () -> Content) { self.title = title; self.content = content() }
    var body: some View {
        Section { content } header: { Text(title).foregroundStyle(GuideTheme.secondary) }
    }
}
