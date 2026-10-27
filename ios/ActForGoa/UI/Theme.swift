import SwiftUI
import UIKit

enum GuideTheme {
    static let paper = adaptive(0xF7F8FC, 0x121622)
    static let ink = adaptive(0x212747, 0xF1F3FF, highLight: 0x11162B, highDark: 0xFFFFFF)
    static let tint = adaptive(0x314BC7, 0xB3C0FF, highLight: 0x2037A2, highDark: 0xD6DEFF)
    static let onTint = adaptive(0xFFFFFF, 0x212747)
    static let secondary = adaptive(0x566079, 0xB7C0D8, highLight: 0x39435A, highDark: 0xD9E0F2)
    static let surface = adaptive(0xFFFFFF, 0x1E2536)
    static let citrus = adaptive(0xE6F28C, 0x303B21)
    static let lilac = adaptive(0xE5DEFF, 0x342E4B)
    static let coral = adaptive(0xFFDBC9, 0x4B302A)
    static let aqua = adaptive(0xC9EDE7, 0x203E3C)
    static let sky = adaptive(0xD5E8FF, 0x26364D)
    static let rose = adaptive(0xF7DCEE, 0x442D40)

    private static func adaptive(_ light: UInt32, _ dark: UInt32, highLight: UInt32? = nil, highDark: UInt32? = nil) -> Color {
        Color(UIColor { traits in
            let high = traits.accessibilityContrast == .high
            let value = traits.userInterfaceStyle == .dark ? (high ? highDark ?? dark : dark) : (high ? highLight ?? light : light)
            return UIColor(red: CGFloat((value >> 16) & 255) / 255, green: CGFloat((value >> 8) & 255) / 255, blue: CGFloat(value & 255) / 255, alpha: 1)
        })
    }
    static func topicColor(_ topic: String?) -> Color {
        switch topic {
        case "Waste & recycling", "Food & farming": citrus
        case "Nature & wildlife", "Water & environment": aqua
        case "Community & rights": lilac
        case "Culture & heritage": coral
        case "Health & wellbeing": rose
        default: sky
        }
    }
    static func topicSymbol(_ topic: String?) -> String {
        guard let topic, let index = GuideTopics.all.firstIndex(of: topic) else { return "book.closed" }
        return GuideTopics.symbols[index]
    }
    static let display = Font.system(.largeTitle, design: .rounded, weight: .bold)
    static let heading = Font.system(.title2, design: .rounded, weight: .bold)
}

struct TopicLabel: View {
    let topic: String
    var body: some View {
        Label(topic, systemImage: GuideTheme.topicSymbol(topic))
            .font(.subheadline.weight(.semibold)).foregroundStyle(GuideTheme.ink)
            .padding(.horizontal, 12).padding(.vertical, 8)
            .background(GuideTheme.topicColor(topic), in: RoundedRectangle(cornerRadius: 12))
            .fixedSize(horizontal: false, vertical: true)
    }
}

struct SectionHeading: View {
    let title: String
    var body: some View {
        Text(title).font(GuideTheme.heading).foregroundStyle(GuideTheme.ink)
            .accessibilityAddTraits(.isHeader).frame(maxWidth: .infinity, alignment: .leading)
    }
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
        Label { Text(text).fixedSize(horizontal: false, vertical: true) } icon: { Image(systemName: "info.circle") }
            .font(.subheadline).foregroundStyle(GuideTheme.secondary)
            .frame(maxWidth: .infinity, alignment: .leading).padding(18)
            .background(GuideTheme.surface, in: RoundedRectangle(cornerRadius: 18))
    }
}

extension View {
    func guideList() -> some View {
        self.scrollContentBackground(.hidden).background(GuideTheme.paper)
            .listStyle(.insetGrouped).tint(GuideTheme.tint)
    }
    func readingWidth() -> some View { self.frame(maxWidth: 680, alignment: .leading).frame(maxWidth: .infinity) }
    func catalogueRow() -> some View {
        self.listRowBackground(Color.clear).listRowSeparator(.hidden)
            .listRowInsets(EdgeInsets(top: 10, leading: 20, bottom: 10, trailing: 20))
    }
}

struct GuideSection<Content: View>: View {
    let title: String
    let content: Content
    init(_ title: String, @ViewBuilder content: () -> Content) { self.title = title; self.content = content() }
    var body: some View {
        Section { content } header: { Text(title).foregroundStyle(GuideTheme.secondary) }
    }
}
