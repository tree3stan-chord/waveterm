Name:           waveterm
Version:        0.2.0
Release:        1%{?dist}
Summary:        A modern terminal-based music visualizer with stunning ASCII art effects

License:        MIT
URL:            https://github.com/espadonne/waveterm
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel >= 3.8
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
Requires:       python3 >= 3.8
Requires:       python3-numpy
Requires:       python3-click
Requires:       python3-rich
Requires:       python3-pydantic
Requires:       python3-toml

%description
WaveTerm is a modern terminal-based music visualizer inspired by web audio visualizers.
Perfect for headless servers, development environments, and live performances.

Features:
- 15+ stunning visualizations (Basic, Advanced, and Extreme modes)
- Perfect for headless servers with simulated audio patterns
- Multiple input sources: microphone, audio files, or simulated audio
- Modern CLI interface with Rich formatting
- Plugin architecture for custom visualizations
- Export capabilities for saving frames, GIFs, and videos
- Cross-platform support: Linux, macOS, Windows

Visualization modes include frequency bars, matrix rain, particle fields,
starfield warp, ASCII flames, 4D hypercubes, fractal trees, dimensional
portals, and much more.

%prep
%autosetup

%build
# Build wheel from pyproject.toml
%{python3} -m pip wheel --no-deps --wheel-dir dist .

%install
%{python3} -m pip install --root %{buildroot} --no-deps --ignore-installed dist/*.whl

%files
%doc README.md
%license LICENSE
%{python3_sitelib}/%{name}/
%{python3_sitelib}/%{name}-%{version}*.dist-info/
%{_bindir}/waveterm
%{_bindir}/waveterm-demo

%changelog
* Mon Jan 27 2025 espadonne (mfw) <espadonne@outlook.com> - 0.2.0-1
- Initial RPM release
- 15 stunning visualization modes (basic, advanced, extreme)
- Perfect for headless servers with audio simulation
- Modern CLI with Rich formatting and Click commands
- Plugin architecture for extensibility
- Export capabilities framework
- Cross-platform Python package with optional dependencies