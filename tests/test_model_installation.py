import pytest

import app


@pytest.mark.parametrize(
    ("installed_packages", "reinstall_models", "should_install"),
    [
        ([], False, True),
        ([object()], False, False),
        ([object()], True, True),
    ],
)
def test_load_local_models_install_policy(
    tmp_path, monkeypatch, installed_packages, reinstall_models, should_install
):
    model_path = tmp_path / "custom.argosmodel"
    model_path.touch()
    (tmp_path / "not-a-model.txt").touch()

    monkeypatch.setattr(app, "MODELS_DIR", str(tmp_path))
    monkeypatch.setattr(
        app.argostranslate.package,
        "get_installed_packages",
        lambda: installed_packages,
    )
    installed_paths = []
    monkeypatch.setattr(
        app.argostranslate.package,
        "install_from_path",
        installed_paths.append,
    )

    app.load_local_models(reinstall_models=reinstall_models)

    assert installed_paths == ([str(model_path)] if should_install else [])
