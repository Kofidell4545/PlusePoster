# 🚀 Welcome to PlusePoster!

🎉 Are you tired of manually posting content on social media? PlusePoster is here to help! This friendly Python tool makes it easy to automate your social media posts across multiple platforms. Whether you're a creator, marketer, or business owner, PlusePoster streamlines your workflow with robust scheduling and seamless integration.

## 🎯 What You Can Do With PlusePoster
- 📱 Post text, images, and videos
- 📅 Schedule posts for any time
- 🤝 Support for Twitter, Instagram, and Facebook
- 🔄 Automatic media uploads
- 🔒 Secure credential management
- 🔄 Easy to use and extend 

**Our Mission:** Make social media automation accessible to everyone—whether you’re a tech expert or a non-technical user. PlusePoster is built so anyone can use it effortlessly, no matter their background.

---

## ✨ Features

- **Open Source for All:** Free to use, adapt, and improve—by creators, for creators and businesses worldwide.
- **Simple, User-Friendly Experience:** Easy setup with step-by-step guides; no coding knowledge needed.
- **Multi-Platform Support:** Automate posts to Twitter (X), Instagram, Facebook, and easily extend to new platforms.
- **Rich Media Automation:** Schedule and publish text, image, and video content.
- **Smart Scheduling:** Custom post times, recurring campaigns, and time zone–aware scheduling.
- **Secure Credentials:** Environment variables and encrypted secrets for safe API management.
- **Modular & Extensible:** Add new platforms or content types with minimal effort.
- **AI-Ready:** Easily integrates with AI content generators and LLMs.
- **Developer-Friendly:** Type-annotated, well-documented codebase, with CI and unit tests.
- **Community Driven:** Contributions, ideas, and feedback are welcome from all over the world!

---

## 🚀 Quickstart

### 1. Prerequisites

- Python 3.10+
- [pipx](https://pipx.pypa.io) (recommended) or pip
- Social media API credentials (see docs per platform)

### 2. Installation

```bash
git clone https://github.com/Kofidell4545/PlusePoster.git
cd PlusePoster
pip install -r requirements.txt
```

Or install in an isolated environment:
```bash
pipx install .
```

### 3. Configuration

Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your API keys and secrets
```

Alternatively, use a `config.yaml` for advanced multi-account setups. See [docs/config.md](docs/config.md).

---

## 🛠️ Usage

**No programming required!** Use our simple CLI or graphical interface (coming soon), or integrate with your own tools if you wish.

Post a video to Twitter:
```python
from pluseposter import PlusePoster

# Create a poster instance
pp = PlusePoster()

# Twitter examples
pp.post(
    platform="twitter",
    content_type="text",
    content="🚀 New Feature Launch! #AI #Automation"
)

pp.post(
    platform="twitter",
    content_type="image",
    file_path="media/image.jpg",
    caption="Check out our new feature!"
)

# Instagram examples
pp.post(
    platform="instagram",
    content_type="image",
    file_path="media/instagram.jpg",
    caption="New Instagram post! 📸"
)

pp.post(
    platform="instagram",
    content_type="video",
    file_path="media/instagram.mp4",
    caption="Video post on Instagram! 🎬"
)

# Facebook examples
pp.post(
    platform="facebook",
    content_type="text",
    content="New update on Facebook!"
)

pp.post(
    platform="facebook",
    content_type="image",
    file_path="media/facebook.jpg",
    caption="Image post on Facebook! 📸"
)
```

Schedule a post:
```python
pp.schedule_post(
    platform="instagram",
    content_type="image",
    file_path="media/launch.jpg",
    caption="We're live on Instagram! 🌟",
    scheduled_time="2025-06-30T10:00:00Z"
)
```

Or use the CLI for quick tasks:
```bash
# Post to Twitter
python -m pluseposter --platform twitter --type text --caption "Hello Twitter! 🐦"

# Post to Instagram
python -m pluseposter --platform instagram --type image --file "media/instagram.jpg" --caption "New Instagram post! 📸"

# Post to Facebook
python -m pluseposter --platform facebook --type text --caption "Hello Facebook! 👋"

# Schedule a post
python -m pluseposter --platform twitter --type text --caption "Scheduled post!" --schedule "2025-07-01T09:00:00Z"
```

---

## 📚 Documentation

- [Full API Reference](docs/api.md)
- [Configuration Guide](docs/config.md)
- [Extending PlusePoster](docs/extending.md)
- [FAQ](docs/faq.md)

---

## ✅ Modern, Accessible, and Secure

- [x] Async I/O for speed and scalability
- [x] Type hints & Pydantic for data validation
- [x] .env & secrets management (never commit credentials!)
- [x] Pytest & GitHub Actions for reliability
- [x] Modular, extensible architecture
- [x] Semantic versioning & clear changelogs

---

## 🤝 Contributing

We love community contributions! Whether you’re a developer, a content creator, a business owner, or a social media enthusiast, your feedback and improvements are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) and open an issue or PR.

---

## 📄 License

MIT License © 2025 [Kofidell4545](https://github.com/Kofidell4545)

---

## 🌏 Open for Everyone

PlusePoster is open source so that creators and businesses around the world can use, adapt, and improve it. Our goal is to empower everyone to automate their social media, without barriers—no matter where you are or your technical background. Join the community and make social automation easier for all!
