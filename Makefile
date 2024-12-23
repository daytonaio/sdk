# Get version from root package.json
VERSION := $(shell node -p "require('./package.json').version")

.PHONY: sync-version build-all build-docs publish-all clean

# Sync versions across packages
sync-version:
	@echo "Syncing version $(VERSION) across packages..."
	@node -e "const p=require('./packages/typescript/package.json'); p.version='$(VERSION)'; require('fs').writeFileSync('./packages/typescript/package.json', JSON.stringify(p,null,2))"
	@echo "Updated TypeScript package version to $(VERSION)"
	@sed -i.bak 's/version = ".*"/version = "$(VERSION)"/' packages/python/pyproject.toml && rm packages/python/pyproject.toml.bak
	@echo "Updated Python package version to $(VERSION)"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf packages/typescript/dist
	@rm -rf packages/python/dist packages/python/build packages/python/*.egg-info

# Build docs for both packages
build-docs:
	@echo "Building documentation..."
	@cd packages/typescript && npm run docs
	@cd packages/python && npm run docs

# Build both packages and docs
build-all: clean sync-version
	@echo "Building all packages..."
	@cd packages/typescript && npm run build
	@cd packages/python && python -m build
	@$(MAKE) build-docs

# Publish both packages
publish-all: build-all
	@echo "Publishing all packages..."
	@cd packages/typescript && npm publish
	@cd packages/python && python -m twine upload dist/*