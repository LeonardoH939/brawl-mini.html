from pathlib import Path

root = Path("HyperDroidPC")

# Branding only. Keep com.winlator package/application id because native Winlator paths
# are hard-coded to it in several components.
build = root / "app/build.gradle"
txt = build.read_text()
txt = txt.replace('versionCode 33', 'versionCode 34')
txt = txt.replace('versionName "11.2"', 'versionName "0.1.0-hyperdroid"')
build.write_text(txt)

strings = root / "app/src/main/res/values/strings.xml"
txt = strings.read_text()
txt = txt.replace('<string name="app_name">Winlator</string>', '<string name="app_name">HyperDroid PC</string>')
txt = txt.replace('<string name="shortcuts">Shortcuts</string>', '<string name="shortcuts">Apps de PC</string>')
txt = txt.replace('<string name="containers">Containers</string>', '<string name="containers">Ambientes de PC</string>')
txt = txt.replace('<string name="input_controls">Input Controls</string>', '<string name="input_controls">Controles</string>')
txt = txt.replace('<string name="settings">Settings</string>', '<string name="settings">Configurações</string>')
txt = txt.replace('<string name="about">About</string>', '<string name="about">Sobre</string>')
insert = '''\n    <string name="hyper_home">Início</string>
    <string name="hyper_android_apps">Apps Android</string>
    <string name="hyper_pc_apps">Apps de PC</string>
    <string name="hyper_pc_env">Ambientes de PC</string>
    <string name="hyper_store">Loja Android</string>
    <string name="hyper_store_missing">Instale o HyperDroid Store/Aptoide para abrir a loja.</string>
    <string name="hyper_desktop_subtitle">Android + programas de Windows em uma só tela</string>
'''
txt = txt.replace('</resources>', insert + '</resources>')
strings.write_text(txt)

manifest = root / "app/src/main/AndroidManifest.xml"
txt = manifest.read_text()
queries = '''\n    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN"/>
            <category android:name="android.intent.category.LAUNCHER"/>
        </intent>
        <package android:name="cm.aptoide.pt"/>
    </queries>
'''
txt = txt.replace('    <application\n', queries + '\n    <application\n', 1)
old_filter = '''            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>'''
new_filter = old_filter + '''\n            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.HOME"/>
                <category android:name="android.intent.category.DEFAULT"/>
            </intent-filter>'''
txt = txt.replace(old_filter, new_filter, 1)
manifest.write_text(txt)

menu = root / "app/src/main/res/menu/main_menu.xml"
txt = menu.read_text()
txt = txt.replace(
    '<group android:checkableBehavior="single">\n',
    '<group android:checkableBehavior="single">\n        <item android:icon="@drawable/icon_shortcut" android:id="@+id/menu_item_hyper_home" android:title="@string/hyper_home" />\n',
    1
)
menu.write_text(txt)

desktop = root / "app/src/main/java/com/winlator/DesktopFragment.java"
desktop.write_text(r'''package com.winlator;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.GridLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class DesktopFragment extends Fragment {
    private int dp(Context context, int value) {
        return Math.round(value * context.getResources().getDisplayMetrics().density);
    }

    private TextView label(Context context, String text, float size, boolean bold) {
        TextView view = new TextView(context);
        view.setText(text);
        view.setTextSize(size);
        view.setTextColor(Color.WHITE);
        if (bold) view.setTypeface(view.getTypeface(), android.graphics.Typeface.BOLD);
        return view;
    }

    private View action(Context context, String title, String subtitle, View.OnClickListener listener) {
        LinearLayout box = new LinearLayout(context);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(context, 16), dp(context, 14), dp(context, 16), dp(context, 14));
        box.setBackgroundColor(Color.rgb(42, 46, 55));
        box.setOnClickListener(listener);

        TextView t = label(context, title, 17f, true);
        TextView s = label(context, subtitle, 12f, false);
        s.setTextColor(Color.LTGRAY);
        box.addView(t);
        box.addView(s);

        GridLayout.LayoutParams lp = new GridLayout.LayoutParams();
        lp.width = 0;
        lp.height = ViewGroup.LayoutParams.WRAP_CONTENT;
        lp.columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f);
        lp.setMargins(dp(context, 6), dp(context, 6), dp(context, 6), dp(context, 6));
        box.setLayoutParams(lp);
        return box;
    }

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle state) {
        Context context = requireContext();
        ScrollView scroll = new ScrollView(context);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.rgb(18, 21, 26));

        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(context, 18), dp(context, 18), dp(context, 18), dp(context, 24));

        TextView title = label(context, "HyperDroid PC", 30f, true);
        TextView subtitle = label(context, getString(R.string.hyper_desktop_subtitle), 14f, false);
        subtitle.setTextColor(Color.LTGRAY);
        root.addView(title);
        root.addView(subtitle);

        GridLayout actions = new GridLayout(context);
        actions.setColumnCount(2);
        LinearLayout.LayoutParams actionsLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        actionsLp.topMargin = dp(context, 14);
        actions.setLayoutParams(actionsLp);

        MainActivity activity = (MainActivity) requireActivity();
        actions.addView(action(context, getString(R.string.hyper_pc_apps), "Atalhos do Wine / Winlator",
                v -> activity.showFragment(new ShortcutsFragment())));
        actions.addView(action(context, getString(R.string.hyper_pc_env), "Criar e configurar ambiente Windows",
                v -> activity.showFragment(new ContainersFragment())));
        actions.addView(action(context, getString(R.string.input_controls), "Teclado, mouse e gamepad",
                v -> activity.showFragment(new InputControlsFragment(0))));
        actions.addView(action(context, getString(R.string.hyper_store), "Abrir o HyperDroid Store",
                v -> openStore(context)));
        root.addView(actions);

        TextView androidTitle = label(context, getString(R.string.hyper_android_apps), 20f, true);
        LinearLayout.LayoutParams titleLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        titleLp.topMargin = dp(context, 22);
        androidTitle.setLayoutParams(titleLp);
        root.addView(androidTitle);

        GridLayout appGrid = new GridLayout(context);
        appGrid.setColumnCount(4);
        LinearLayout.LayoutParams gridLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        gridLp.topMargin = dp(context, 8);
        appGrid.setLayoutParams(gridLp);
        loadAndroidApps(context, appGrid);
        root.addView(appGrid);

        scroll.addView(root);
        return scroll;
    }

    private void openStore(Context context) {
        PackageManager pm = context.getPackageManager();
        Intent intent = pm.getLaunchIntentForPackage("cm.aptoide.pt");
        if (intent != null) {
            startActivity(intent);
        } else {
            Toast.makeText(context, R.string.hyper_store_missing, Toast.LENGTH_LONG).show();
        }
    }

    private void loadAndroidApps(Context context, GridLayout grid) {
        PackageManager pm = context.getPackageManager();
        Intent query = new Intent(Intent.ACTION_MAIN);
        query.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> apps = new ArrayList<>(pm.queryIntentActivities(query, 0));
        Collections.sort(apps, Comparator.comparing(a -> a.loadLabel(pm).toString().toLowerCase()));

        for (ResolveInfo info : apps) {
            if (info.activityInfo == null) continue;
            String pkg = info.activityInfo.packageName;
            if (pkg.equals(context.getPackageName())) continue;

            LinearLayout item = new LinearLayout(context);
            item.setGravity(Gravity.CENTER);
            item.setOrientation(LinearLayout.VERTICAL);
            item.setPadding(dp(context, 6), dp(context, 10), dp(context, 6), dp(context, 10));

            Drawable drawable = info.loadIcon(pm);
            ImageView icon = new ImageView(context);
            icon.setImageDrawable(drawable);
            LinearLayout.LayoutParams iconLp = new LinearLayout.LayoutParams(dp(context, 52), dp(context, 52));
            icon.setLayoutParams(iconLp);

            TextView name = label(context, info.loadLabel(pm).toString(), 11f, false);
            name.setGravity(Gravity.CENTER);
            name.setMaxLines(2);

            item.addView(icon);
            item.addView(name);
            item.setOnClickListener(v -> {
                Intent launch = pm.getLaunchIntentForPackage(pkg);
                if (launch != null) startActivity(launch);
            });

            GridLayout.LayoutParams lp = new GridLayout.LayoutParams();
            lp.width = 0;
            lp.height = ViewGroup.LayoutParams.WRAP_CONTENT;
            lp.columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f);
            item.setLayoutParams(lp);
            grid.addView(item);
        }
    }
}
''')

main = root / "app/src/main/java/com/winlator/MainActivity.java"
txt = main.read_text()

old = '''            boolean showShortcutsFirst = preferences.getBoolean("show_shortcuts_first", false);
            int selectedMenuItemId = intent.getIntExtra("selected_menu_item_id", 0);
            int menuItemId = selectedMenuItemId > 0 ? selectedMenuItemId : (showShortcutsFirst ? R.id.menu_item_shortcuts : R.id.menu_item_containers);

            actionBar.setHomeAsUpIndicator(R.drawable.icon_action_bar_menu);
            onNavigationItemSelected(navigationView.getMenu().findItem(menuItemId));
            navigationView.setCheckedItem(menuItemId);
            if (!requestAppPermissions()) RootFSInstaller.installIfNeeded(this);'''
new = '''            actionBar.setHomeAsUpIndicator(R.drawable.icon_action_bar_menu);
            showFragment(new DesktopFragment());
            navigationView.setCheckedItem(R.id.menu_item_hyper_home);
            if (!requestAppPermissions()) RootFSInstaller.installIfNeeded(this);'''
if old not in txt:
    raise RuntimeError("Could not patch MainActivity startup")
txt = txt.replace(old, new, 1)

old_back = '''            else if (currentFragment instanceof ContainersFragment) {
                finish();
            }
        }

        showFragment(new ContainersFragment());'''
new_back = '''            else if (currentFragment instanceof DesktopFragment) {
                moveTaskToBack(true);
                return;
            }
        }

        showFragment(new DesktopFragment());'''
if old_back not in txt:
    raise RuntimeError("Could not patch MainActivity back behavior")
txt = txt.replace(old_back, new_back, 1)

old_switch = '''        switch (item.getItemId()) {
            case R.id.menu_item_shortcuts:'''
new_switch = '''        switch (item.getItemId()) {
            case R.id.menu_item_hyper_home:
                showFragment(new DesktopFragment());
                break;
            case R.id.menu_item_shortcuts:'''
if old_switch not in txt:
    raise RuntimeError("Could not patch MainActivity navigation")
txt = txt.replace(old_switch, new_switch, 1)
main.write_text(txt)

notice = root / "HYPERDROID-NOTES.md"
notice.write_text("""# HyperDroid PC 0.1

Android launcher-style derivative built on Winlator.

Goals:
- Android HOME launcher UI
- Android app drawer
- PC app shortcuts through the Winlator engine
- PC environment management
- optional launch shortcut for the HyperDroid Store/Aptoide package cm.aptoide.pt

Important:
The previous PocketLinux/Debian/PRoot UI is not part of this build.
Winlator still includes its own minimal rootfs/glibc runtime internally because Wine/Box64
need it. It is an implementation detail, not a user-facing Linux desktop.

Upstream: https://github.com/brunodev85/winlator
License: LGPL-2.1 (see bundled LICENSE)
""")
