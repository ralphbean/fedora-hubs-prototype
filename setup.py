""" Setup file for fedora hubs """

from setuptools import setup, find_packages


def get_description():
    with open('README.rst', 'r') as f:
        return ''.join(f.readlines()[2:])


def get_requirements():
    with open('requirements.txt', 'r') as f:
        return [l.strip() for l in f.readlines() if l.strip()]


setup(
    name='fedora-hubs',
    version='0.0.1',
    description='A community portal for fedora contributors and you!',
    long_description=get_description(),
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url="https://github.com/ralphbean/fedora-hubs-prototype",
    download_url="https://pypi.python.org/pypi/fedora-hubs/",
    license='AGPLv3+',
    install_requires=get_requirements(),
    #tests_require=tests_require,
    #test_suite='nose.collector',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    entry_points={
        'moksha.consumer': [
            "cache_invalidator = hubs.consumer:CacheInvalidatorExtraordinaire",
        ],
    },
)
