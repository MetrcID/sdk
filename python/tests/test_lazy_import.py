# Copyright 2025 Metrc, LLC
# SPDX-License-Identifier: MIT
"""``import retailid`` must work without ``requests`` installed (QR-only use)."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

SRC = str(Path(__file__).resolve().parents[1] / "src")


def _run(code: str) -> subprocess.CompletedProcess[str]:
    # sys.modules["requests"] = None makes any `import requests` raise ImportError,
    # simulating an environment where requests is not installed.
    prelude = f"import sys\nsys.path.insert(0, {SRC!r})\nsys.modules['requests'] = None\n"
    return subprocess.run(
        [sys.executable, "-c", prelude + textwrap.dedent(code)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_qr_functions_work_without_requests() -> None:
    result = _run(
        """
        import retailid
        from retailid import RetailIdPair, get_short_url, load_config, RetailIdApiError

        pair = RetailIdPair("HTTPS://D.1A4.COM/10NOIEYKAJDG6CF0EXGJL")
        assert pair.index == 1
        assert get_short_url(pair.batch_id, pair.index, domain="d.1a4.com")
        assert "retailid.api" not in sys.modules
        """
    )
    assert result.returncode == 0, result.stderr


def test_api_client_without_requests_raises_helpful_error() -> None:
    result = _run(
        """
        try:
            from retailid import RetailIdClient
        except ImportError as e:
            assert "retailid[api]" in str(e), e
        else:
            raise AssertionError("expected ImportError")
        """
    )
    assert result.returncode == 0, result.stderr


def test_api_names_load_lazily() -> None:
    import retailid
    from retailid import api

    assert retailid.RetailIdClient is api.RetailIdClient
    assert "RetailIdClient" in dir(retailid)
    for name in retailid.__all__:
        assert hasattr(retailid, name), name
