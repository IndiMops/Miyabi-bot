"""Guards against fragile image links in embed definitions."""

import re
import unittest
from pathlib import Path

EMBEDS_DIR = Path(__file__).resolve().parent.parent / "embeds"

# Signed attachment links expire and only keep working while Discord re-signs
# them; wiki images must live on a stable host (Cloudinary).
DISCORD_ATTACHMENT_URL = re.compile(
    r"(?:media|cdn)\.discordapp\.(?:net|com)/attachments/"
)


class EmbedImageLinkTests(unittest.TestCase):
    def test_embeds_do_not_use_discord_attachment_links(self) -> None:
        offenders = []
        for path in sorted(EMBEDS_DIR.rglob("*.py")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if DISCORD_ATTACHMENT_URL.search(line):
                    offenders.append(f"{path.relative_to(EMBEDS_DIR.parent)}:{number}")

        self.assertEqual(offenders, [], "Discord attachment links found in embeds")


if __name__ == "__main__":
    unittest.main()
