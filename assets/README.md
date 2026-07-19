# assets

Static images for the profile README (banners, architecture diagrams).

Dark-mode rule: every image that has theme-dependent colors ships in two
variants and is embedded with a `<picture>` tag so it renders correctly in
both GitHub themes:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagram-dark.png">
  <img src="assets/diagram-light.png" alt="Architecture">
</picture>
```

Currently all visuals are generated services (typing SVG, stats cards) which
handle theming via URL params, so this folder is empty by design.
