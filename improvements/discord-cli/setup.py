from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-discord",
    version="1.0.0",
    description="Message read/send control for the Discord desktop client (CDP)",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-discord=cli_anything.discord.discord_cli:main",
        ],
    },
    package_data={
        "cli_anything.discord": ["skills/*.md", "utils/cdp_client.mjs"],
    },
    include_package_data=True,
    python_requires=">=3.10",
)
