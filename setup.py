from setuptools import setup


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="pytraceplot",
    version="0.1",
    description="Plot CPU and other traces using matplotlib",
    long_description=readme(),
    url="https://github.com/adobke/pytraceplot",
    author="Alistair Dobke",
    license="MIT",
    packages=["pytraceplot"],
    install_requires=["matplotlib"],
    zip_safe=False,
    test_suite="nose.collector",
    tests_require=["nose"],
)
