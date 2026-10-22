import SwiftUI
import MessageUI

struct ContactView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    private enum Field: Hashable { case name, email, message }
    @FocusState private var focusedField: Field?
    @State private var draft: EmailDraft
    @State private var prepared = false
    @State private var compose = false
    @State private var discard = false
    @State private var feedback: String?
    init(entry: String = "", involve: Bool = false) {
        _draft = State(initialValue: EmailDraft(reason: entry.isEmpty ? (involve ? "Volunteer with ActForGoa" : "Ask a question") : "Suggest a correction", entry: entry))
    }
    private var dirty: Bool { !draft.name.isEmpty || !draft.email.isEmpty || !draft.message.isEmpty }
    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Text("Share a local initiative, update an entry, or tell us what you’re looking for.")
                    Text("Prepare an email, then review and send it yourself. Nothing is sent by this form.").font(.subheadline).foregroundStyle(GuideTheme.secondary)
                }
                GuideSection("Your details") {
                    TextField("Your name", text: $draft.name).textContentType(.name).focused($focusedField, equals: .name).submitLabel(.next).onSubmit { focusedField = .email }.accessibilityIdentifier("contact-name")
                    TextField("Email address", text: $draft.email).textContentType(.emailAddress).keyboardType(.emailAddress).textInputAutocapitalization(.never).autocorrectionDisabled().focused($focusedField, equals: .email).submitLabel(.next).onSubmit { focusedField = .message }.accessibilityIdentifier("contact-email")
                }
                GuideSection("Your message") {
                    Picker("I’d like to", selection: $draft.reason) {
                        ForEach(["Ask a question", "Suggest a correction", "List an organisation", "Share a story or resource", "Volunteer with ActForGoa"], id: \.self) { Text($0) }
                    }
                    if !draft.entry.isEmpty { Text("About: \(draft.entry)").font(.subheadline).foregroundStyle(GuideTheme.secondary) }
                    TextField("Include useful details and links", text: $draft.message, axis: .vertical).lineLimit(5...12).focused($focusedField, equals: .message).accessibilityIdentifier("contact-message")
                    Text("\(draft.message.count)/4,000 characters").font(.caption).foregroundStyle(draft.message.count > 4000 ? Color.red : GuideTheme.secondary)
                }
                Section {
                    Button("Prepare email") { focusedField = nil; prepared = true; feedback = nil }.disabled(!draft.valid).accessibilityIdentifier("prepare-email")
                    if !draft.valid && dirty { Text("Add your name, a valid email address, and a message of up to 4,000 characters.").font(.subheadline).foregroundStyle(GuideTheme.secondary) }
                    if prepared {
                        Text("Your email is ready to review.").font(.headline)
                        Text("Nothing has been sent yet.").font(.subheadline).foregroundStyle(GuideTheme.secondary)
                        Button("Review in email") {
                            if MFMailComposeViewController.canSendMail() { compose = true }
                            else if let url = draft.mailURL {
                                openURL(url) { accepted in
                                    if !accepted { feedback = "No email app is available. Copy the prepared email below and send it to info@actforgoa.org." }
                                }
                            }
                        }
                        ShareLink(item: "To: info@actforgoa.org\nSubject: \(draft.reason)\n\n\(draft.body)") { Label("Copy or share prepared email", systemImage: "square.and.arrow.up") }
                    }
                    if let feedback { Text(feedback).font(.subheadline) }
                }
                Section {
                    Link("info@actforgoa.org", destination: URL(string: "mailto:info@actforgoa.org")!)
                    Link("WhatsApp: +91 85548 33885", destination: URL(string: "https://wa.me/918554833885")!)
                    Link("WhatsApp: +91 98239 12012", destination: URL(string: "https://wa.me/919823912012")!)
                    Text("1 Design Valley\nAlto Povorim 403521, Goa")
                    Link("Original contact page", destination: URL(string: "https://actforgoa.org/contact-us/")!)
                } header: { Text("Get in touch directly").foregroundStyle(GuideTheme.secondary) } footer: { Text("Published contact details; please confirm they are current.") }
            }.guideList().textCase(nil).scrollDismissesKeyboard(.interactively).navigationTitle("Contact ActForGoa").navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Cancel") { if dirty { discard = true } else { dismiss() } } } }
                .onChange(of: draft) { prepared = false; feedback = nil }
                .confirmationDialog("Discard this message?", isPresented: $discard, titleVisibility: .visible) {
                    Button("Discard message", role: .destructive) { dismiss() }
                    Button("Keep writing", role: .cancel) {}
                }
        }
        .interactiveDismissDisabled(dirty)
        .sheet(isPresented: $compose) {
            MailComposer(draft: draft) { result in
                compose = false
                switch result {
                case .sent: feedback = "Your email was handed to Mail for delivery."
                case .saved: feedback = "Your email was saved in Mail."
                case .failed: feedback = "Mail couldn’t send the email. Your message is still here."
                default: feedback = "Nothing was sent. Your message is still here."
                }
            }
        }
    }
}

struct MailComposer: UIViewControllerRepresentable {
    let draft: EmailDraft
    let completion: (MFMailComposeResult) -> Void
    func makeCoordinator() -> Coordinator { Coordinator(completion: completion) }
    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let c = MFMailComposeViewController(); c.mailComposeDelegate = context.coordinator
        c.setToRecipients(["info@actforgoa.org"]); c.setSubject(draft.reason); c.setMessageBody(draft.body, isHTML: false)
        return c
    }
    func updateUIViewController(_ c: MFMailComposeViewController, context: Context) {}
    final class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let completion: (MFMailComposeResult) -> Void
        init(completion: @escaping (MFMailComposeResult) -> Void) { self.completion = completion }
        func mailComposeController(_ controller: MFMailComposeViewController, didFinishWith result: MFMailComposeResult, error: Error?) { completion(error == nil ? result : .failed) }
    }
}
