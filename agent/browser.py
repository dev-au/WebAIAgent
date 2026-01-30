import toons
import json
import html_to_json
from playwright.async_api import async_playwright


class Browser:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self, headless=False):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        # Add the JWT cookie if needed - users might want this configurable
        await self.context.add_cookies(
            [
                {
                    "name": "jwt",
                    "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk2MjgxNTEsImlkIjoiNjJhM2U4MTAxODk0Yjc1ZjdhYTA1N2IzIiwib3JpZ19pYXQiOjE3Njk1ODQ5NTF9.rytjte9Vr8aRYpNdnebRdI1cGxv-eN9Y_xeU46Bnp6o",
                    "domain": "staging.hippo.uz",
                    "path": "/",
                }
            ]
        )
        self.page = await self.context.new_page()

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def goto(self, url):
        await self.page.goto(url, wait_until="networkidle", timeout=300000)

    async def get_ui_state(self):
        # Wait for the page to be reasonably stable
        try:
            await self.page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass

        await self.page.evaluate("""(() => {
  const CLICKABLE_SELECTOR = `
    a[href],
    button,
    [role="button"],
    [role="menuitem"],
    [onclick],
    input[type="button"],
    input[type="submit"],
    input:not([type="hidden"]),
    textarea,
    [contenteditable="true"],
    [role="textbox"],
    [role="searchbox"],
    [role="combobox"]
  `;

  function domPath(el, depth = 4) {
    const path = [];
    while (el && path.length < depth) {
      let name = el.tagName.toLowerCase();
      if (el.id) name += `#${el.id}`;
      path.unshift(name);
      el = el.parentElement;
    }
    return path.join(">");
  }

  async function hash(str) {
    const buf = await crypto.subtle.digest(
      "SHA-256",
      new TextEncoder().encode(str)
    );
    return [...new Uint8Array(buf)]
      .slice(0, 6)
      .map(b => b.toString(16).padStart(2, "0"))
      .join("");
  }

  async function annotate(el) {
    if (el.dataset.aiId) return;
    const fp = [
      el.tagName.toLowerCase(),
      el.getAttribute("role") || "",
      el.innerText?.trim().slice(0, 50) || "",
      el.getAttribute("href") || "",
      domPath(el)
    ].join("|");
    el.dataset.aiId = await hash(fp);
  }

  // annotate existing elements
  (async () => {
    const els = document.querySelectorAll(CLICKABLE_SELECTOR);
    for (const el of els) await annotate(el);
  })();

  // observe new elements
  new MutationObserver(muts => {
    muts.forEach(m =>
      m.addedNodes.forEach(n => {
        if (n.nodeType !== 1) return;
        if (n.matches(CLICKABLE_SELECTOR)) annotate(n);
        n.querySelectorAll?.(CLICKABLE_SELECTOR).forEach(el => annotate(el));
      })
    );
  }).observe(document.body, { childList: true, subtree: true });
})();
""")

        html_string = await self.page.content()
        return html_string
        output_json = html_to_json.convert(html_string)
        cleaned_json = self.clear_json(output_json)
        return toons.dumps(cleaned_json)

    async def click(self, target):
        if not self.page:
            return "Error: Page not initialized."

        selector = f'[data-ai-id="{target}"]'

        try:
            await self.page.click(selector, timeout=1500, force=True)
            return f"Successfully clicked {selector}"
        except Exception:
            raise Exception(f"Could not find element with target: {target}")

    async def clear(self, target):
        if not self.page:
            return "Error: Page not initialized."

        locator = self.page.locator(f'[data-ai-id="{target}"]')
        try:
            await locator.click(timeout=1500, force=True)
            await locator.fill("")
            await locator.dispatch_event("input")
            await locator.dispatch_event("change")
            return f"Successfully cleared {target}"
        except Exception as e:
            raise Exception(f"Failed to clear {target}: {str(e)}")

    async def type(self, target, value):
        if not self.page:
            return "Error: Page not initialized."

        locator = self.page.locator(f'[data-ai-id="{target}"]')

        try:
            # Focus and clear before typing
            await locator.click(timeout=1500, force=True)
            await locator.fill("")

            # Human-like typing is more reliable for certain event listeners
            await locator.press_sequentially(str(value), delay=15)

            # Ensure all events are fired
            await locator.dispatch_event("input")
            await locator.dispatch_event("change")
            await locator.dispatch_event("blur")
            return f"Successfully typed '{value}' into {target}"
        except Exception as e:
            # Fallback to fill if sequential typing fails
            try:
                await locator.fill(str(value), timeout=1500)
                await locator.dispatch_event("input")
                await locator.dispatch_event("change")
                return f"Successfully filled '{value}' into {target}"
            except Exception:
                raise Exception(f"Failed to type/fill into {target}: {str(e)}")

    def clear_json(self, data):
        if isinstance(data, dict):
            new_data = {}
            for k, v in data.items():
                if k.lower() in [
                    "svg",
                    "script",
                    "style",
                    "path",
                    "symbol",
                    "defs",
                    "g",
                    "meta",
                    "link",
                    "head",
                    "_comment",
                ]:
                    continue

                if k == "_attributes":
                    if isinstance(v, dict):
                        essential_attrs = [
                            "name",
                            "type",
                            "value",
                            "placeholder",
                            "aria-label",
                            "aria-labelledby",
                            "role",
                            "data-ai-id",
                            "title",
                            "alt",
                            "src",
                        ]
                        v = {
                            attr_k: attr_v
                            for attr_k, attr_v in v.items()
                            if attr_k.lower() in essential_attrs
                        }
                        if not v:
                            continue
                        new_data[k] = v
                    continue

                cleared_v = self.clear_json(v)

                if cleared_v is not None:
                    if isinstance(cleared_v, (dict, list)) and not cleared_v:
                        continue
                    new_data[k] = cleared_v

            return new_data if new_data else None

        elif isinstance(data, list):
            new_list = []
            for item in data:
                cleared_item = self.clear_json(item)
                if cleared_item is not None:
                    if isinstance(cleared_item, (dict, list)) and not cleared_item:
                        continue
                    new_list.append(cleared_item)
            return new_list if new_list else None
        else:
            return data
