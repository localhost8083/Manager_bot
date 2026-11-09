"""Chain-fallback self-check. Run: python tests_brain.py — must exit 0.
Stubs discord (not needed for brain_reply) and urllib to simulate upstreams."""
import json, sys, types, time, urllib.request

# stub discord module so bot.py imports without the real package
disc = types.ModuleType("discord")
disc.Intents = types.SimpleNamespace(default=lambda: types.SimpleNamespace(message_content=False))
def _event(fn):
    return fn

tree = types.SimpleNamespace(command=lambda **kw: (lambda fn: fn))
disc.Client = type("Client", (object,), {"__init__": lambda self, *a, **k: None, "run": lambda self, *a, **k: None, "event": lambda self, fn: fn, "tree": tree})
disc.Activity = object
disc.ActivityType = types.SimpleNamespace(watching=0)
disc.Message = object
disc.AllowedMentions = object
disc.Forbidden = type("Forbidden", (Exception,), {})
disc.errors = types.SimpleNamespace(
    PrivilegedIntentsRequired=type("PIR", (Exception,), {}),
    LoginFailure=type("LF", (Exception,), {}),
)
sys.modules["discord"] = disc
ext = types.ModuleType("discord.ext")
cmds = types.ModuleType("discord.ext.commands")
cmds.Bot = disc.Client  # bot.py uses commands.Bot (commands.Client doesn't exist in discord.py 2.x)
ext.commands = cmds
sys.modules["discord.ext"] = ext
sys.modules["discord.ext.commands"] = cmds

import bot

calls = []


class R:
    def __init__(self, payload):
        self.p = payload

    def read(self):
        return json.dumps(self.p).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def fake_urlopen(req, timeout=0):
    model = json.loads(req.data.decode())["model"]
    calls.append(model)
    if model == "empty":
        return R({"choices": [{"message": {"content": ""}}]})  # the 200-empty fault
    if model == "bad":
        raise urllib.error.HTTPError("u", 502, "Bad Gateway", {}, None)
    return R({"choices": [{"message": {"content": "  hello  "}}]})


bot.CFG = {"brain": {"base_url": "https://x/v1", "api_key": "k", "models": ["empty", "bad", "good"]}}

urllib.request.urlopen = fake_urlopen
assert bot.brain_reply("q", "u", "c1") == "hello", "failover to good"
assert calls == ["empty", "bad", "good"], calls

# cooldown: empty+bad cooling, second call goes straight to good
calls.clear()
assert bot.brain_reply("q", "u", "c1") == "hello"
assert calls == ["good"], calls

# cooldown expiry
bot._BRAIN_COOL["empty"] = time.monotonic() - 1
calls.clear()
assert bot.brain_reply("q", "u", "c1") == "hello"
assert calls == ["empty", "good"], calls

# all cooling -> cooldowns clear, everything retried
bot._BRAIN_COOL["empty"] = bot._BRAIN_COOL["good"] = time.monotonic() + 999
calls.clear()
assert bot.brain_reply("q", "u", "c1") == "hello"
assert calls == ["empty", "bad", "good"], calls

# legacy single-model config behaves as before
bot.CFG = {"brain": {"base_url": "https://x/v1", "api_key": "k", "model": "good"}}
bot._BRAIN_COOL.clear()
calls.clear()
assert bot.brain_reply("q", "u", "c1") == "hello"
assert calls == ["good"], calls

# total failure raises
bot.CFG = {"brain": {"base_url": "https://x/v1", "api_key": "k", "models": ["bad"]}}
bot._BRAIN_COOL.clear()
try:
    bot.brain_reply("q", "u", "c1")
    raise SystemExit("should have raised")
except Exception:
    pass

# image attachment: multimodal content parts on the wire
seen = {}
def fake_img(req, timeout=0):
    seen["body"] = json.loads(req.data.decode())
    seen["auth"] = req.headers.get("Authorization")
    return R({"choices": [{"message": {"content": "I see it"}}]})
urllib.request.urlopen = fake_img
bot.CFG = {"brain": {"base_url": "https://x/v1/", "api_key": "k9", "models": ["good"]}}
bot._BRAIN_COOL.clear()
out = bot.brain_reply("what is this", "u", "c1", image_urls=["data:image/png;base64,AAA"])
assert out == "I see it"
content = seen["body"]["messages"][-1]["content"]
assert seen["body"]["model"] == "good"
assert isinstance(content, list) and len(content) == 2, content
assert content[0]["type"] == "text" and "what is this" in content[0]["text"]
assert content[1]["type"] == "image_url" and content[1]["image_url"]["url"].startswith("data:image/png")
assert seen["auth"] == "Bearer k9"

print("PASS brain chain (failover, empty-200, cooldown, retry-all, legacy, raise, vision)")
