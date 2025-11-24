# KSAMM_TOML

> Current as of KSAMM v0.1.5a

The `ksamm.toml` file is a file used to give information to KSA Mod Manager about your mod.

What you can list:
- Dependencies
- Optional Dependencies
- Metadata

the `ksamm.toml` should be put in the main folder for your mod. Here is an example for the folder format:

```js
PolarEarth/
├──Textures/
├──mod.toml
├──ksamm.toml
└── ...
```

Here is a sample `ksamm.toml`:

```toml
[[dependencies]]
name = "<name1>"
link = "<link1>"

[[dependencies]]
name = "<name2>"
link = "<link2>"

[[optional_dependencies]]
name = "<name3>"
link = "<link3>"

[[optional_dependencies]]
name = "<name4>"
link = "<link4>"

[metadata]
name = "Example Mod"
version = "1.5.1"
author = "Awsomgamr999"
description = "Adds an example to the GitHub"
tags = ["GitHub", "Example", "Informative"]
license_name = "MIT"
license_description = "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in...
update_path = "https://spacedock.info/mod/4050/KSA%20Discord%20Rich%20Presence/download"
```

Planned Features:
- Config Section for developers to specify configurations for their mods

If you have any issues or want to suggest a feature for `ksamm.toml` ping me on discord at `@Awsomgamr999`
