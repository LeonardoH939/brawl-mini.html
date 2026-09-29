from pathlib import Path

root = Path("PocketLinux")

gradle = root / "app/build.gradle"
txt = gradle.read_text()
txt = txt.replace('applicationId "io.github.lord1egypt.prootx"', 'applicationId "com.pocketlinux.mobile"')
txt = txt.replace('versionName "1.0.0"', 'versionName "1.0.3-autosetup"')
gradle.write_text(txt)

manifest = root / "app/src/main/AndroidManifest.xml"
txt = manifest.read_text()
txt = txt.replace(
    'android:authorities="io.github.lord1egypt.prootx.documents"',
    'android:authorities="com.pocketlinux.mobile.documents"'
)
manifest.write_text(txt)

main_activity = root / "app/src/main/java/io/github/lord1egypt/prootx/MainActivity.kt"
txt = main_activity.read_text()
txt = txt.replace(
    """        if (contributionPrompter.viewShouldBeShown()) {
            contributionPrompter.showView()
        }""",
    """        if (BuildConfig.ENABLE_PLAY_SERVICES && contributionPrompter.viewShouldBeShown()) {
            contributionPrompter.showView()
        }"""
)
txt = txt.replace(
    """    override fun onResume() {
        super.onResume()
        billingManager.querySubPurchases()
        billingManager.queryInAppPurchases()
        viewModel.handleOnResume()
    }""",
    """    override fun onResume() {
        super.onResume()
        if (BuildConfig.ENABLE_PLAY_SERVICES) {
            try {
                billingManager.querySubPurchases()
                billingManager.queryInAppPurchases()
            } catch (_: Exception) {
            }
        }
        viewModel.handleOnResume()
    }"""
)
txt = txt.replace(
    """    override fun onDestroy() {
        billingManager.destroy()
        super.onDestroy()
    }""",
    """    override fun onDestroy() {
        if (BuildConfig.ENABLE_PLAY_SERVICES) {
            try {
                billingManager.destroy()
            } catch (_: Exception) {
            }
        }
        super.onDestroy()
    }"""
)
main_activity.write_text(txt)

permissions = root / "app/src/main/java/io/github/lord1egypt/prootx/utils/PermissionHandler.kt"
txt = permissions.read_text()
txt = txt.replace(
    """        fun permissionsAreGranted(context: Context): Boolean {
            return (ContextCompat.checkSelfPermission(context,
                    Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED &&

                    ContextCompat.checkSelfPermission(context,
                            Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED)
        }""",
    """        fun permissionsAreGranted(context: Context): Boolean {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) return true
            return (ContextCompat.checkSelfPermission(context,
                    Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED &&
                    ContextCompat.checkSelfPermission(context,
                            Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED)
        }"""
)
permissions.write_text(txt)

notifications = root / "app/src/main/java/io/github/lord1egypt/prootx/utils/NotificationConstructor.kt"
txt = notifications.read_text()
txt = txt.replace(
    """        val pendingSessionListIntent = PendingIntent
                .getActivity(context, 0, sessionListIntent, 0)""",
    """        val immutableFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0
        val pendingSessionListIntent = PendingIntent
                .getActivity(context, 0, sessionListIntent, immutableFlag)"""
)
txt = txt.replace(
    """        val stopSessionsPendingIntent = PendingIntent
                .getService(context, 0, stopSessionsIntent, PendingIntent.FLAG_UPDATE_CURRENT)""",
    """        val stopSessionsPendingIntent = PendingIntent
                .getService(context, 0, stopSessionsIntent, PendingIntent.FLAG_UPDATE_CURRENT or immutableFlag)"""
)
txt = txt.replace(
    """        val settingsPendingIntent = PendingIntent
                .getActivity(context, 0, settingsIntent, 0)""",
    """        val settingsPendingIntent = PendingIntent
                .getActivity(context, 0, settingsIntent, immutableFlag)"""
)
notifications.write_text(txt)

strings = root / "app/src/main/res/values/strings.xml"
txt = strings.read_text()
txt = txt.replace("ProotX", "PocketLinux")
txt = txt.replace("Welcome to PocketLinux!", "Bem-vindo ao PocketLinux!")
strings.write_text(txt)

pt = root / "app/src/main/res/values-pt-rBR"
pt.mkdir(parents=True, exist_ok=True)
(pt / "strings.xml").write_text("""<resources>
    <string name="app_name">PocketLinux</string>
    <string name="welcome">Bem-vindo ao PocketLinux!</string>
    <string name="apps">Aplicativos</string>
    <string name="sessions">Sessões</string>
    <string name="filesystems">Sistemas Linux</string>
    <string name="settings">Configurações</string>
    <string name="help">Ajuda</string>
    <string name="button_continue">Continuar</string>
    <string name="save">Salvar</string>
    <string name="add">Adicionar</string>
    <string name="delete">Excluir</string>
    <string name="refresh">Atualizar</string>
    <string name="hint_username">Usuário</string>
    <string name="hint_password">Senha</string>
    <string name="hint_vnc_password">Senha VNC</string>
    <string name="progress_downloading">Baixando os arquivos necessários…</string>
    <string name="progress_setting_up_filesystem">Configurando o Linux…</string>
    <string name="progress_starting">Iniciando…</string>
    <string name="service_notification_title">PocketLinux</string>
    <string name="service_notification_description">PocketLinux está executando um serviço Linux.</string>
</resources>""")

(root / "POCKETLINUX-NOTES.md").write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3 autosetup:
- avoid Google Play Billing initialization in sideload/debug builds
- Android 11+ storage permission compatibility
- immutable PendingIntent flags for Android 12+
- PocketLinux branding and Brazilian Portuguese essentials
""")


# Diagnostic launcher that survives crashes from the legacy runtime.
src = root / "app/src/main/java/io/github/lord1egypt/prootx"
(src / "PocketLinuxApp.kt").write_text(r'''package io.github.lord1egypt.prootx

import android.app.Application
import android.util.Log
import java.io.PrintWriter
import java.io.StringWriter

class PocketLinuxApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val previous = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            try {
                val sw = StringWriter()
                throwable.printStackTrace(PrintWriter(sw))
                getSharedPreferences("diagnostics", MODE_PRIVATE)
                    .edit()
                    .putString("last_crash", sw.toString())
                    .putLong("last_crash_time", System.currentTimeMillis())
                    .apply()
                Log.e("PocketLinux", "Uncaught crash", throwable)
            } catch (_: Throwable) {
            }
            previous?.uncaughtException(thread, throwable)
        }
    }
}
''')

(src / "DiagnosticActivity.kt").write_text(r'''package io.github.lord1egypt.prootx

import android.app.Activity
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Typeface
import android.os.Build
import android.os.Bundle
import android.text.method.ScrollingMovementMethod
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast

class DiagnosticActivity : Activity() {
    private lateinit var crashText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val pad = (20 * resources.displayMetrics.density).toInt()
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }

        val scroll = ScrollView(this)
        val title = TextView(this).apply {
            text = "PocketLinux • diagnóstico"
            textSize = 24f
            setTypeface(typeface, Typeface.BOLD)
        }
        root.addView(title)

        val info = TextView(this).apply {
            text = "Android ${Build.VERSION.RELEASE} (SDK ${Build.VERSION.SDK_INT})\n" +
                    "ABI: ${Build.SUPPORTED_ABIS.joinToString()}\n\n" +
                    "Esta tela segura serve para identificar exatamente onde o motor Linux está falhando."
            textSize = 15f
        }
        root.addView(info)

        val start = Button(this).apply {
            text = "INICIAR POCKETLINUX"
            setOnClickListener {
                getSharedPreferences("diagnostics", MODE_PRIVATE)
                    .edit().remove("last_crash").apply()
                startActivity(Intent(this@DiagnosticActivity, MainActivity::class.java))
            }
        }
        root.addView(start)

        val copy = Button(this).apply {
            text = "COPIAR ÚLTIMO ERRO"
            setOnClickListener { copyCrash() }
        }
        root.addView(copy)

        crashText = TextView(this).apply {
            textSize = 12f
            typeface = Typeface.MONOSPACE
            setTextIsSelectable(true)
            movementMethod = ScrollingMovementMethod()
        }
        root.addView(crashText)

        scroll.addView(root)
        setContentView(scroll)
        showCrash()
    }

    override fun onResume() {
        super.onResume()
        showCrash()
    }

    private fun showCrash() {
        val crash = getSharedPreferences("diagnostics", MODE_PRIVATE)
            .getString("last_crash", null)
        crashText.text = if (crash.isNullOrBlank()) {
            "\nNenhum erro capturado ainda. Toque em INICIAR POCKETLINUX."
        } else {
            "\nÚLTIMO ERRO CAPTURADO:\n\n$crash"
        }
    }

    private fun copyCrash() {
        val crash = getSharedPreferences("diagnostics", MODE_PRIVATE)
            .getString("last_crash", null)
        if (crash.isNullOrBlank()) {
            Toast.makeText(this, "Nenhum erro capturado.", Toast.LENGTH_SHORT).show()
            return
        }
        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText("PocketLinux crash", crash))
        Toast.makeText(this, "Erro copiado.", Toast.LENGTH_SHORT).show()
    }
}
''')

manifest = root / "app/src/main/AndroidManifest.xml"
txt = manifest.read_text()
txt = txt.replace(
    '<application\n        android:allowBackup="false"',
    '<application\n        android:name=".PocketLinuxApp"\n        android:allowBackup="false"'
)
txt = txt.replace(
    '''        <activity android:name=".MainActivity" android:launchMode="singleTask">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <action android:name="android.intent.action.VIEW" />

                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>


            <nav-graph android:value="@navigation/nav_graph"/>
        </activity>''',
    '''        <activity android:name=".DiagnosticActivity" android:launchMode="singleTask">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity android:name=".MainActivity" android:launchMode="singleTask">
            <nav-graph android:value="@navigation/nav_graph"/>
        </activity>'''
)
manifest.write_text(txt)


# PocketLinux 1.0.3: automatic first-time Debian setup.
# The packages are downloaded inside the Linux filesystem on first creation,
# keeping the APK reasonably small while removing the need to type setup commands.
filesystem_manager = root / "app/src/main/java/io/github/lord1egypt/prootx/utils/FilesystemManager.kt"
fm = filesystem_manager.read_text()

old_copy = r'''        files?.let {
            for (file in files) {
                if (file.name.contains("rootfs") && filesystem.isCreatedFromBackup) continue
                val targetFile = File("${targetDirectory.absolutePath}/${file.name}")
                file.copyTo(targetFile, overwrite = true)
                prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, file.name)
            }
        }
    }

    fun removeRootfsFilesFromFilesystem'''
new_copy = r'''        files?.let {
            for (file in files) {
                if (file.name.contains("rootfs") && filesystem.isCreatedFromBackup) continue
                val targetFile = File("${targetDirectory.absolutePath}/${file.name}")
                file.copyTo(targetFile, overwrite = true)
                prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, file.name)
            }
        }

        val setupScript = File(targetDirectory, "pocketlinuxBootstrap.sh")
        setupScript.writeText("""#!/bin/sh
MARKER=/var/lib/pocketlinux/.setup-v1-complete
if [ -f "${' ]; then
    echo "PocketLinux: configuracao inicial ja concluida."
    exit 0
fi

echo "PocketLinux: preparando instalacao automatica..."
mkdir -p /var/lib/pocketlinux /var/tmp/pocketlinux-apt
chmod 1777 /var/tmp/pocketlinux-apt
export TMPDIR=/var/tmp/pocketlinux-apt
export DEBIAN_FRONTEND=noninteractive

apt-get update || exit 20
dpkg --configure -a || true
apt-get -f install -y || true

PACKAGES="ca-certificates curl wget git nano unzip zip p7zip-full gnupg htop file tree build-essential gcc g++ make cmake pkg-config gdb python3 python3-pip python3-venv python3-dev default-jdk nodejs npm xfce4 xfce4-goodies thunar mousepad xterm dbus-x11 firefox-esr ffmpeg vlc gimp ristretto file-roller mesa-utils libgl1-mesa-dri dosbox scummvm"

echo "PocketLinux: instalando ambiente de programacao, desktop e aplicativos..."
apt-get install -y ${' || {
    echo "PocketLinux: primeira tentativa falhou; atualizando indices e tentando novamente..."
    apt-get update || exit 21
    apt-get install -y $PACKAGES || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "$MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER" ]; then
    echo "PocketLinux: configuracao inicial ja concluida."
    exit 0
fi

echo "PocketLinux: preparando instalacao automatica..."
mkdir -p /var/lib/pocketlinux /var/tmp/pocketlinux-apt
chmod 1777 /var/tmp/pocketlinux-apt
export TMPDIR=/var/tmp/pocketlinux-apt
export DEBIAN_FRONTEND=noninteractive

apt-get update || exit 20
dpkg --configure -a || true
apt-get -f install -y || true

PACKAGES="ca-certificates curl wget git nano unzip zip p7zip-full gnupg htop file tree build-essential gcc g++ make cmake pkg-config gdb python3 python3-pip python3-venv python3-dev default-jdk nodejs npm xfce4 xfce4-goodies thunar mousepad xterm dbus-x11 firefox-esr ffmpeg vlc gimp ristretto file-roller mesa-utils libgl1-mesa-dri dosbox scummvm"

echo "PocketLinux: instalando ambiente de programacao, desktop e aplicativos..."
apt-get install -y $PACKAGES || {
    echo "PocketLinux: primeira tentativa falhou; atualizando indices e tentando novamente..."
    apt-get update || exit 21
    apt-get install -y $PACKAGES || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "${'
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}PACKAGES || {
    echo "PocketLinux: primeira tentativa falhou; atualizando indices e tentando novamente..."
    apt-get update || exit 21
    apt-get install -y ${' || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "$MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER" ]; then
    echo "PocketLinux: configuracao inicial ja concluida."
    exit 0
fi

echo "PocketLinux: preparando instalacao automatica..."
mkdir -p /var/lib/pocketlinux /var/tmp/pocketlinux-apt
chmod 1777 /var/tmp/pocketlinux-apt
export TMPDIR=/var/tmp/pocketlinux-apt
export DEBIAN_FRONTEND=noninteractive

apt-get update || exit 20
dpkg --configure -a || true
apt-get -f install -y || true

PACKAGES="ca-certificates curl wget git nano unzip zip p7zip-full gnupg htop file tree build-essential gcc g++ make cmake pkg-config gdb python3 python3-pip python3-venv python3-dev default-jdk nodejs npm xfce4 xfce4-goodies thunar mousepad xterm dbus-x11 firefox-esr ffmpeg vlc gimp ristretto file-roller mesa-utils libgl1-mesa-dri dosbox scummvm"

echo "PocketLinux: instalando ambiente de programacao, desktop e aplicativos..."
apt-get install -y $PACKAGES || {
    echo "PocketLinux: primeira tentativa falhou; atualizando indices e tentando novamente..."
    apt-get update || exit 21
    apt-get install -y $PACKAGES || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "${'
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}PACKAGES || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "$MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER" ]; then
    echo "PocketLinux: configuracao inicial ja concluida."
    exit 0
fi

echo "PocketLinux: preparando instalacao automatica..."
mkdir -p /var/lib/pocketlinux /var/tmp/pocketlinux-apt
chmod 1777 /var/tmp/pocketlinux-apt
export TMPDIR=/var/tmp/pocketlinux-apt
export DEBIAN_FRONTEND=noninteractive

apt-get update || exit 20
dpkg --configure -a || true
apt-get -f install -y || true

PACKAGES="ca-certificates curl wget git nano unzip zip p7zip-full gnupg htop file tree build-essential gcc g++ make cmake pkg-config gdb python3 python3-pip python3-venv python3-dev default-jdk nodejs npm xfce4 xfce4-goodies thunar mousepad xterm dbus-x11 firefox-esr ffmpeg vlc gimp ristretto file-roller mesa-utils libgl1-mesa-dri dosbox scummvm"

echo "PocketLinux: instalando ambiente de programacao, desktop e aplicativos..."
apt-get install -y ${' || {
    echo "PocketLinux: primeira tentativa falhou; atualizando indices e tentando novamente..."
    apt-get update || exit 21
    apt-get install -y $PACKAGES || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "${'
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}PACKAGES || {
    echo "PocketLinux: primeira tentativa falhou; atualizando indices e tentando novamente..."
    apt-get update || exit 21
    apt-get install -y ${' || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "${'
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}PACKAGES || exit 22
}

apt-get autoremove -y || true
apt-get autoclean || true
touch "${'
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
}MARKER"
echo "PocketLinux: configuracao automatica concluida."
exit 0
""".trimIndent())
        prootxFiles.makePermissionsUsable(targetDirectory.absolutePath, setupScript.name)
    }

    fun removeRootfsFilesFromFilesystem'''

if old_copy not in fm:
    raise RuntimeError("Could not patch copyAssetsToFilesystem for PocketLinux autosetup")
fm = fm.replace(old_copy, new_copy, 1)

old_extract = r'''        return@withContext busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )
    }'''
new_extract = r'''        val extractionResult = busyboxExecutor.executeProotCommand(
            command,
            filesystemDirName,
            commandShouldTerminate = true,
            env = env,
            listener = listener
        )

        if (extractionResult is SuccessfulExecution && filesystem.distributionType.toLowerCase().contains("debian")) {
            listener("\nPocketLinux: iniciando configuracao automatica. Isso acontece apenas na primeira instalacao...\n")
            val setupResult = busyboxExecutor.executeProotCommand(
                "/support/pocketlinuxBootstrap.sh",
                filesystemDirName,
                commandShouldTerminate = true,
                env = env,
                listener = listener
            )
            if (setupResult !is SuccessfulExecution) {
                return@withContext setupResult
            }
        }

        return@withContext extractionResult
    }'''

if old_extract not in fm:
    raise RuntimeError("Could not patch extractFilesystem for PocketLinux autosetup")
fm = fm.replace(old_extract, new_extract, 1)
filesystem_manager.write_text(fm)

notes = root / "POCKETLINUX-NOTES.md"
notes.write_text("""# PocketLinux 1.0.3 autosetup
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.3:
- automatic Debian first-time setup; no manual apt commands required
- installs programming tools, XFCE, Firefox ESR, multimedia and utility packages
- uses /var/tmp/pocketlinux-apt instead of the Android cache for apt temporary files
- setup runs once and records /var/lib/pocketlinux/.setup-v1-complete
- keeps Android 11+ storage, Android 12+ PendingIntent and sideload billing compatibility fixes
- PocketLinux branding and Brazilian Portuguese essentials

The Linux packages are downloaded during first environment creation rather than bundled
inside the APK. This keeps the APK smaller and lets apt choose packages for the device architecture.
""")
