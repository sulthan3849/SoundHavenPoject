# Vite & React Tool Gotchas

Prevent agent-induced syntax errors during code editing in Vite/React projects.

## Template Literals Escaping
When using code modification tools (like `write_to_file` or `replace_file_content`) to inject TypeScript/JavaScript containing template literals (backticks `` ` `` and interpolation `${}`), **DO NOT** escape them with backslashes (`\`). 
The system handles JSON stringification natively. Adding manual backslashes causes Vite (via the OXC parser) to instantly crash with `[PARSE_ERROR] Invalid Unicode escape sequence`.

## Next.js vs Vite Compatibility
**Never** use Next.js specific components like `next/image` (`<Image />`) in this project since it is built with Vite. 
Always convert imported Next.js components to standard HTML `<img>` tags.
