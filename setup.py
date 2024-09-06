from setuptools import setup, find_packages

setup(
    name="sweet_indulgence_order_manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask",
        "xmlrpc",
        "PyYAML",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "extract-orders=sweet_indulgence_order_manager.extract_odoo_orders:main",
            "create-labels=sweet_indulgence_order_manager.get_data_for_delhivery:main",
            "order-gui=sweet_indulgence_order_manager.gui_script:main",
        ],
    },
    author="Vaidish Sumaria",
    author_email="vaidishsumaria101@gmail.com",
    description="A package for managing Sweet Indulgence orders and creating shipping labels",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/heenaSI/sweet_indulgence_order_manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)