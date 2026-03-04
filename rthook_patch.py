"""
PyInstaller 运行时钩子 — 补丁加载器
====================================
如果 exe 旁边有 patch/ 目录, 里面的 .py 文件会覆盖打包时的冻结代码。
优先级: patch/ > 冻结代码

补丁目录结构示例:
  patch/
    config.py            ← 覆盖 config 模块
    core/
      bot.py             ← 覆盖 core.bot
    gui/
      app.py             ← 覆盖 gui.app
"""
import sys
import os
import importlib
import importlib.util


def _setup_patch():
    if not getattr(sys, 'frozen', False):
        return

    app_dir = os.path.dirname(sys.executable)
    patch_dir = os.path.join(app_dir, 'patch')

    if not os.path.isdir(patch_dir):
        return

    class _PatchFinder:
        """在 FrozenImporter 之前拦截, 从 patch/ 加载 .py"""

        def find_spec(self, fullname, path, target=None):
            parts = fullname.split('.')

            pkg_init = os.path.join(patch_dir, *parts, '__init__.py')
            if os.path.isfile(pkg_init):
                return importlib.util.spec_from_file_location(
                    fullname, pkg_init,
                    submodule_search_locations=[
                        os.path.join(patch_dir, *parts)
                    ],
                )

            if len(parts) > 1:
                mod_file = os.path.join(
                    patch_dir, *parts[:-1], parts[-1] + '.py'
                )
            else:
                mod_file = os.path.join(patch_dir, parts[0] + '.py')

            if os.path.isfile(mod_file):
                return importlib.util.spec_from_file_location(
                    fullname, mod_file
                )

            return None

    sys.meta_path.insert(0, _PatchFinder())

    n = sum(
        1 for r, _, fs in os.walk(patch_dir)
        for f in fs if f.endswith('.py')
    )
    print(f"[补丁] 已加载 patch/ 目录 ({n} 个文件)")


_setup_patch()
