package ro.ase.ie.dma06.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import androidx.appcompat.app.AppCompatActivity;
import ro.ase.ie.dma06.R;

/** Opens each step of the demo. */
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        openOnClick(R.id.btnStep1, SingleColumnActivity.class);
        openOnClick(R.id.btnStep2, TwoColumnActivity.class);
        openOnClick(R.id.btnStep3, RecyclerViewActivity.class);
    }

    private void openOnClick(int buttonId, Class<?> activityClass) {
        View button = findViewById(buttonId);
        button.setOnClickListener(v -> startActivity(new Intent(this, activityClass)));
    }
}
