# Mesonconfig

**Mesonconfig** is a terminal-based configuration tool for Meson projects, inspired by the Linux `menuconfig` interface. It provides an interactive way to manage configuration options defined in a KConfig-style file and generate usable outputs.

**This project is in alpha.**

## Installation

```bash
pip install mesonconfig
```

Or install from source:

```bash
git clone https://github.com/Stellcel-Remeny/mesonconfig
cd mesonconfig
pip install -e .
```

## Quick Start

Run Mesonconfig in a directory containing a `KConfig` file:

```bash
mesonconfig
```

Defaults:

* Input: `KConfig`
* Output: `local.conf`

## Features

* Interactive terminal UI (Textual-based)
* KConfig-style configuration system
* Nested menus and dependency handling
* Supports:

  * Boolean options
  * String options
  * Integer options
* Generate `meson_options.txt` for Meson

## CLI Overview

```bash
mesonconfig [OPTIONS] [kconfig_file]
```

### Options

| Option                  | Description                  |
| ----------------------- | ---------------------------- |
| `--kconfig-file <file>` | Path to KConfig file         |
| `--output-file <file>`  | Output config file           |
| `--build-meson-options` | Generate `meson_options.txt` |
| `--verbose`             | Enable debug messages        |
| `--version`             | Show version                 |

For more, view `--help`

## TUI Controls

* Arrow keys -> Navigate
* Enter / Space -> Select / toggle
* ESC -> Back
* ESC ESC -> Exit

## Status & Stability

This project is currently in **alpha**:

* Features may change
* Bugs are expected
* Interfaces are not yet stable
