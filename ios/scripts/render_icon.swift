import AppKit
let size = NSSize(width: 1024, height: 1024)
let image = NSImage(size: size)
image.lockFocus()
NSColor(red: 0.086, green: 0.247, blue: 0.212, alpha: 1).setFill()
NSRect(origin: .zero, size: size).fill()
let text = "a" as NSString
let attributes: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: 800, weight: .bold),
    .foregroundColor: NSColor(red: 0.969, green: 0.969, blue: 0.933, alpha: 1)
]
let bounds = text.size(withAttributes: attributes)
text.draw(at: NSPoint(x: (1024 - bounds.width) / 2 - 30, y: (1024 - bounds.height) / 2 + 65), withAttributes: attributes)
NSColor(red: 0.925, green: 0.847, blue: 0.514, alpha: 1).setFill()
NSBezierPath(ovalIn: NSRect(x: 725, y: 235, width: 80, height: 80)).fill()
image.unlockFocus()
let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))

let resize = Process()
resize.executableURL = URL(fileURLWithPath: "/usr/bin/sips")
resize.arguments = ["-z", "1024", "1024", CommandLine.arguments[1]]
try resize.run()
resize.waitUntilExit()
