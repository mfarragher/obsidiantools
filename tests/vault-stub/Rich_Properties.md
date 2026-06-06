---
title: Rich Properties Example
date: 2025-07-17
time: 2025-07-17T15:30:00
status: In Progress
tags: [obsidian, test, properties]
mixed bag: [1, "two", true, null, '', None]
nested:
  key1: value1
  key2:
    subkey1: nested value
    subkey2: another value
priority: High
links:
  - [[another-note]]
  - [[yet-another-note|custom link text]]
---

prop with spaces:: special value
property:with:colons:: complex:value:here
number:: 42
empty:: 

This is an example note demonstrating various property types supported by Obsidian:

1. Frontmatter properties:
   - Date and time (datetime objects)
   - Arrays (tags)
   - Nested objects
   - Simple key-value pairs

2. Inline properties:
   - Properties with spaces
   - Properties with special characters
   - Number values
   - Empty values