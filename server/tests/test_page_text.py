from app.services.page_text import html_to_text


def test_page_text_keeps_the_article_and_drops_scripts_nav_and_footer():
    html = """
      <html>
        <head>
          <title>Ignored title</title>
          <meta property="og:title" content="Launch notes" />
          <style>.x { color: red }</style>
        </head>
        <body>
          <nav>Home Pricing</nav>
          <script>window.token = "secret-token"</script>
          <article>
            <h1>Launch notes</h1>
            <p>The window opens at 9.</p>
            <p>Bring the checklist.</p>
          </article>
          <footer>Privacy policy</footer>
        </body>
      </html>
    """
    page = html_to_text(html, "https://example.com/launch")
    assert page["title"] == "Launch notes"
    assert "The window opens at 9" in page["text"]
    assert "Bring the checklist" in page["text"]
    assert "secret-token" not in page["text"]
    assert "Privacy policy" not in page["text"]
    assert "Home Pricing" not in page["text"]
    assert "color" not in page["text"]
