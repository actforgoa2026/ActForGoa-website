import XCTest

final class ActForGoaUITests: XCTestCase {
    override func setUpWithError() throws { continueAfterFailure = false }
    func testSearchReadBrowseAndContact() throws {
        let app = XCUIApplication(); app.launch()
        XCTAssertTrue(app.buttons["Snake rescue"].waitForExistence(timeout: 20))
        capture("phone-light", app)
        app.buttons["Snake rescue"].tap()
        let ready = app.staticTexts["Matched by meaning and keywords, on your phone."]
        XCTAssertTrue(ready.waitForExistence(timeout: 30))
        capture("phone-search", app)
        let record = app.buttons["record-resource-590480849c"]
        if !record.isHittable { app.swipeUp() }
        XCTAssertTrue(record.waitForExistence(timeout: 5)); record.tap()
        XCTAssertTrue(app.staticTexts["Snake Rescue Volunteers in Goa"].waitForExistence(timeout: 5))
        capture("phone-reading", app)
        app.tabBars.buttons["Directory"].tap()
        XCTAssertTrue(app.staticTexts["153 results"].waitForExistence(timeout: 5))
        capture("phone-directory", app)
        app.tabBars.buttons["Library"].tap()
        XCTAssertTrue(app.staticTexts["242 results"].waitForExistence(timeout: 5))
        capture("phone-library", app)
        app.tabBars.buttons["Community"].tap()
        capture("phone-community", app)
        reveal(app.buttons["Contact ActForGoa"], in: app).tap()
        XCTAssertTrue(app.textFields["contact-name"].waitForExistence(timeout: 5))
        let prepare = app.buttons["prepare-email"]
        XCTAssertFalse(prepare.isEnabled)
        app.textFields["contact-name"].tap(); app.textFields["contact-name"].typeText("Preview reviewer")
        app.textFields["contact-email"].tap(); app.textFields["contact-email"].typeText("preview@example.org")
        let message = app.textViews["contact-message"]
        if message.exists { message.tap(); message.typeText("Development preview test. No email will be sent.") }
        else { let field = app.textFields["contact-message"]; field.tap(); field.typeText("Development preview test. No email will be sent.") }
        app.swipeUp()
        XCTAssertTrue(prepare.isEnabled); prepare.tap()
        XCTAssertTrue(app.staticTexts["Nothing has been sent yet."].waitForExistence(timeout: 5))
        capture("phone-email-prepared", app)
    }
    func testPracticalGuidesAndTemplates() throws {
        let app = XCUIApplication(); app.launch()
        XCTAssertTrue(app.tabBars.buttons["Library"].waitForExistence(timeout: 20))
        app.tabBars.buttons["Library"].tap()
        let field = app.searchFields.firstMatch
        field.tap(); field.typeText("Krishi Card")
        let guide = app.buttons["record-guide-farming"]
        XCTAssertTrue(guide.waitForExistence(timeout: 20)); guide.tap()
        XCTAssertTrue(app.staticTexts["Start or sustain farming in Goa"].waitForExistence(timeout: 5))
        capture("phone-practical-guide", app)
        let templates = app.buttons["guide-templates"]
        reveal(templates, in: app).tap()
        let item = app.buttons["Farming registration enquiry"]
        reveal(item, in: app).tap()
        XCTAssertTrue(app.buttons["share-guide-file"].waitForExistence(timeout: 5))
        capture("phone-template", app)
        app.buttons["Done"].tap()
        app.swipeUp()
        capture("phone-guide-table", app)
    }
    func testGuideNavigationAndShare() throws {
        let app = XCUIApplication(); app.launch()
        XCTAssertTrue(app.searchFields.firstMatch.waitForExistence(timeout: 20))
        app.searchFields.firstMatch.tap(); app.searchFields.firstMatch.typeText("Krishi Card")
        let guide = app.buttons["record-guide-farming"]
        XCTAssertTrue(guide.waitForExistence(timeout: 20)); guide.tap()
        reveal(app.buttons["See what needs verification"], in: app).tap()
        XCTAssertTrue(app.staticTexts["What still needs verification"].waitForExistence(timeout: 5))
        capture("phone-verification-register", app)
        app.navigationBars.buttons.element(boundBy: 0).tap()
        reveal(app.buttons["On this page"], in: app).tap()
        let section = app.buttons["Choose your first step"]
        reveal(section, in: app).tap()
        capture("phone-guide-section", app)
        XCUIDevice.shared.orientation = .landscapeLeft
        let landscape = NSPredicate { _, _ in app.windows.firstMatch.frame.width > app.windows.firstMatch.frame.height }
        expectation(for: landscape, evaluatedWith: nil)
        waitForExpectations(timeout: 5)
        Thread.sleep(forTimeInterval: 1)
        capture("phone-guide-landscape", app)
        XCUIDevice.shared.orientation = .portrait
        app.terminate(); app.launch()
        app.searchFields.firstMatch.tap(); app.searchFields.firstMatch.typeText("Krishi Card")
        XCTAssertTrue(guide.waitForExistence(timeout: 20)); guide.tap()
        reveal(app.buttons["guide-templates"], in: app).tap()
        let item = app.buttons["Farming registration enquiry"]
        reveal(item, in: app).tap()
        XCTAssertTrue(app.buttons["share-guide-file"].waitForExistence(timeout: 5))
        app.buttons["share-guide-file"].tap()
        XCTAssertTrue(app.buttons["Copy"].waitForExistence(timeout: 15))
        Thread.sleep(forTimeInterval: 1)
        capture("phone-file-share", app)
    }
    func testEmptySearch() throws {
        let app = XCUIApplication(); app.launch()
        let field = app.searchFields.firstMatch
        XCTAssertTrue(field.waitForExistence(timeout: 20)); field.tap(); field.typeText("zzzxqvplm")
        XCTAssertTrue(app.staticTexts["0 results"].waitForExistence(timeout: 20))
        capture("phone-empty", app)
    }
    func testLargeText() throws {
        let app = XCUIApplication()
        app.launchArguments = ["-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"]
        app.launch()
        XCTAssertTrue(app.searchFields.firstMatch.waitForExistence(timeout: 20))
        capture("phone-large-text", app)
        if !app.buttons["Snake rescue"].exists { app.swipeUp() }
        XCTAssertTrue(app.buttons["Snake rescue"].waitForExistence(timeout: 5))
    }
    func testCommunityAndTopicBrowsing() throws {
        let app = XCUIApplication(); app.launch()
        XCTAssertTrue(app.buttons["Snake rescue"].waitForExistence(timeout: 20))
        capture("phone-home", app)
        let topic = app.buttons["topic-Waste & recycling"]
        app.swipeUp()
        reveal(topic, in: app)
        capture("phone-topics", app)
        topic.tap()
        XCTAssertTrue(app.buttons["Clear filters"].waitForExistence(timeout: 5))
        capture("phone-topic-results", app)
        app.buttons["Clear filters"].tap()
        XCTAssertTrue(app.buttons["Snake rescue"].waitForExistence(timeout: 5))
        app.tabBars.buttons["Community"].tap()
        XCTAssertTrue(app.staticTexts["A better Goa starts with us."].waitForExistence(timeout: 5))
        capture("phone-community", app)
        reveal(app.buttons["Contact ActForGoa"], in: app)
        app.swipeUp()
        capture("phone-community-actions", app)
        XCUIDevice.shared.orientation = .landscapeLeft
        let landscape = NSPredicate { _, _ in app.windows.firstMatch.frame.width > app.windows.firstMatch.frame.height }
        expectation(for: landscape, evaluatedWith: nil)
        waitForExpectations(timeout: 8)
        Thread.sleep(forTimeInterval: 2)
        capture("phone-community-landscape", app)
        XCUIDevice.shared.orientation = .portrait
    }
    @discardableResult private func reveal(_ element: XCUIElement, in app: XCUIApplication) -> XCUIElement {
        for _ in 0..<6 {
            if element.exists && element.isHittable { return element }
            app.swipeUp()
        }
        XCTAssertTrue(element.exists && element.isHittable)
        return element
    }
    private func capture(_ name: String, _ app: XCUIApplication) {
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot()); attachment.name = name; attachment.lifetime = .keepAlways; add(attachment)
    }
}
