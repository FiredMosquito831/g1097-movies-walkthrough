package ro.ase.ie.dma03;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ListView;
import android.widget.PopupMenu;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.activity.OnBackPressedCallback;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.GravityCompat;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.navigation.NavigationView;

public class MainActivity extends AppCompatActivity {

    private DrawerLayout drawerLayout;
    private ListView listView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        listView = findViewById(R.id.listView);

        // Long press shows the popup menu
        listView.setOnItemLongClickListener((parent, view, position, id) -> {
            PopupMenu popup = new PopupMenu(this, view);   // anchored to the pressed row
            popup.getMenuInflater().inflate(R.menu.list_item_menu, popup.getMenu());

            popup.setOnMenuItemClickListener(menuItem -> {
                int itemId = menuItem.getItemId();
                String selected = listView.getItemAtPosition(position).toString();

                if (itemId == R.id.action_open) {
                    Toast.makeText(this, "Open: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_rename) {
                    Toast.makeText(this, "Rename: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_delete) {
                    Toast.makeText(this, "Delete: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                }
                return false;
            });

            popup.show();
            return true;   // true = long press handled, so the normal click doesn't also fire
        });


        drawerLayout = findViewById(R.id.drawerLayout);
        MaterialToolbar toolbar = findViewById(R.id.topAppBar);
        NavigationView navigationView = findViewById(R.id.navigationView);


        // Drawer item clicks
        navigationView.setNavigationItemSelectedListener(item -> {
            int id = item.getItemId();

            if (id == R.id.nav_inbox) {
                toolbar.setTitle("Inbox");
            } else if (id == R.id.nav_sent) {
                toolbar.setTitle("Sent");
            } else if (id == R.id.nav_trash) {
                toolbar.setTitle("Trash");
            } else if (id == R.id.nav_settings) {
                Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
            }

            item.setChecked(true);
            drawerLayout.closeDrawer(GravityCompat.START);
            return true;
        });

        // Back button closes the drawer first if it's open
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
                    drawerLayout.closeDrawer(GravityCompat.START);
                } else {
                    setEnabled(false);
                    getOnBackPressedDispatcher().onBackPressed();
                }
            }
        });


        // Hamburger (navigation) icon
        toolbar.setNavigationOnClickListener(v -> {
            drawerLayout.openDrawer(GravityCompat.START);
        });

        // Search, share and overflow menu items
        toolbar.setOnMenuItemClickListener(item -> {
            int id = item.getItemId();

            if (id == R.id.action_search) {
                Toast.makeText(this, "Search", Toast.LENGTH_SHORT).show();
                return true;
            } else if (id == R.id.action_share) {
                Toast.makeText(this, "Share", Toast.LENGTH_SHORT).show();
                return true;
            } else if (id == R.id.action_settings) {
                // open settings
                Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
                return true;
            }
            return false;
        });
    }
}