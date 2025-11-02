import subprocess


def run_applescript(script: str) -> None:
    """
    执行AppleScript
    使用 stdin 传递脚本，避免 -e 多行/转义问题，并开启 check 以捕获非 0 退出码
    """
    try:
        completed = subprocess.run(
            ["osascript"],
            input=script.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        if completed.stdout:
            print(completed.stdout.decode("utf-8", errors="ignore").strip())
    except subprocess.CalledProcessError as e:
        err_out = e.stderr.decode("utf-8", errors="ignore").strip()
        print("AppleScript 执行失败:")
        print(err_out or str(e))
    except Exception as e:
        print(f"执行AppleScript时发生未知错误: {e}")


def call_iphone():
    """
    通过 Bundle ID 获取应用名称，保证在不同语言环境下都能找到正确的进程名称
    然后激活应用，并将第一个窗口移动到指定位置
    """
    apple_script = """
        -- 通过 Bundle ID 获取应用当前语言环境下的名称
        set appName to name of application id "com.apple.ScreenContinuity"
        
        -- 激活应用（通过 Bundle ID，避免本地化名称差异）
        tell application id "com.apple.ScreenContinuity"
            activate
        end tell
        
        -- 使用 UI 脚本移动窗口位置
        tell application "System Events"
            tell process appName
                try
                    set position of window 1 to {1, 50}
                on error errMsg number errNum
                    -- 如果窗口不存在或无权限，输出更清晰的错误提示
                    error "无法设置窗口位置: " & errMsg & " (" & errNum & ")"
                end try
            end tell
        end tell
    """
    run_applescript(apple_script)
