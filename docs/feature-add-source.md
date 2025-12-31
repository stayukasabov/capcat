# Feature Documentation: Automated Source Addition

This document provides an overview of the `./capcat add-source` command, a feature designed to automate the process of adding new RSS-based news sources to the Capcat system.

## 1. Purpose

The primary goal of this feature is to simplify and accelerate the addition of new content sources. It replaces the manual process of creating YAML configuration files with an interactive command-line tool, reducing errors and lowering the barrier for contribution.

## 2. Usage

The command is invoked with a single URL pointing to a valid RSS or Atom feed.

**Syntax:**
```bash
./capcat add-source --url <RSS_FEED_URL>
```

**Example:**
```bash
./capcat add-source --url https://www.theverge.com/rss/index.xml
```

## 3. The Interactive Process

Upon execution, the tool guides the user through a series of prompts to configure the new source:

1.  **Source ID:** The tool inspects the feed to suggest a unique, alphanumeric ID (e.g., `theverge`). The user can accept this suggestion or provide their own.
2.  **Category Assignment:** The user is presented with a list of existing source categories (e.g., `tech`, `news`, `science`) and can assign the new source to one.
3.  **Bundle Integration:** The tool asks if the new source should be added to a pre-existing bundle. If the user agrees, they are shown a list of available bundles (e.g., `tech`, `ai`) to choose from.
4.  **Automated Test:** Finally, the user is prompted to run an immediate test fetch. This test validates that the newly generated configuration works correctly within the Capcat system.

## 4. Automated Actions

Based on the user's input, the command performs the following actions automatically:

*   **Configuration File Generation:** A new YAML file named `<source_id>.yml` is created in `sources/active/config_driven/configs/`. This file contains all the necessary metadata to define the new source, including its name, URL, category, and discovery method (which is set to `rss`).

*   **Bundle Modification:** If a bundle was selected, the `sources/active/bundles.yml` file is safely updated to include the new `source_id` under the chosen bundle, preserving all existing comments and formatting.

*   **Validation:** The command executes the equivalent of `./capcat fetch <source_id> --count 1` to ensure the source is immediately functional. The success or failure of this test is reported directly to the user.

## 5. Core Components

This functionality is powered by a set of new, single-responsibility services:

*   `core.source_system.RssFeedIntrospector`: A service responsible for fetching the provided URL, validating that it is a legitimate RSS/Atom feed, and extracting initial metadata like the feed's title and base URL.

*   `core.source_system.SourceConfigGenerator`: A service that takes the metadata gathered from the introspector and the user prompts to generate the content of the new source's YAML configuration file.

*   `core.source_system.BundleManager`: A service that safely handles reading and writing to the `bundles.yml` file. It uses the `ruamel.yaml` library to ensure that comments, spacing, and the original structure of the file are preserved during modification.
