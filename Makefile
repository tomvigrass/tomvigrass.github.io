# CV Generator Makefile

.PHONY: install generate help

# Default target
help:
	@echo "Available commands:"
	@echo "  install   - Install uv package manager"
	@echo "  generate  - Generate HTML from markdown CV data"
	@echo "  help      - Show this help message"

# Install uv package manager
install:
	@echo "Installing uv package manager..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ uv is already installed"; \
		uv --version; \
	else \
		echo "📦 Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully"; \
	fi

# Generate CV HTML from markdown
generate: install
	@echo "🔍 Checking file dependencies..."
	@if [ ! -f "cv-data.md" ]; then \
		echo "❌ cv-data.md not found"; \
		exit 1; \
	fi
	@if [ ! -f "generate_cv.py" ]; then \
		echo "❌ generate_cv.py not found"; \
		exit 1; \
	fi
	@echo "✅ All dependencies found"
	@echo "🚀 Generating CV HTML..."
	@uv run python generate_cv.py
	@echo "✅ CV generation complete!"