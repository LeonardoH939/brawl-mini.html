from pathlib import Path

root = Path("PocketLinux")

gradle = root / "app/build.gradle"
txt = gradle.read_text()
txt = txt.replace('applicationId "io.github.lord1egypt.prootx"', 'applicationId "com.pocketlinux.mobile"')
txt = txt.replace('versionName "1.0.0"', 'versionName "1.0.1-pocket"')
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

(root / "POCKETLINUX-NOTES.md").write_text("""# PocketLinux 1.0.1
Customized GPLv3 build of ProotX.
Upstream: https://github.com/Lord1Egypt/ProotX

Changes in 1.0.1:
- avoid Google Play Billing initialization in sideload/debug builds
- Android 11+ storage permission compatibility
- immutable PendingIntent flags for Android 12+
- PocketLinux branding and Brazilian Portuguese essentials
""")
