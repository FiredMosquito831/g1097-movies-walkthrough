package ro.ase.ie.dma03;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.util.TypedValue;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;

public class SecondActivity extends AppCompatActivity {

    LinearLayout inflatedLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_second);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        inflatedLayout = findViewById(R.id.main);
    }

    public void btnClick(View view) {
        AlertDialog.Builder builder = new AlertDialog.Builder(SecondActivity.this);
        builder.setTitle("Add new control ...")
                .setMessage("Are you sure you want to add a new control?")
                .setCancelable(true)
                .setPositiveButton("Do it!", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        int id = addButton();
                        Snackbar.make(SecondActivity.this, inflatedLayout, "Cancel previous action.", Snackbar.LENGTH_LONG)
                                .setAction("Cancel", new View.OnClickListener() {
                                    @Override
                                    public void onClick(View v) {
                                        Button viewById = inflatedLayout.findViewById(id);
                                        inflatedLayout.removeView(viewById);
                                    }
                                }).show();

                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        Toast.makeText(SecondActivity.this, "Object creation cancelled", Toast.LENGTH_LONG).show();
                    }
                });
        builder.show();
    }


    int counter = 0;
    public int addButton()
    {
        DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
        int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50,
                displayMetrics);

        Button newBtn = new Button(SecondActivity.this);
        newBtn.setText("Button_" + (++counter));
        newBtn.setId(counter);

        ViewGroup.LayoutParams layoutParams =
                new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT);
        newBtn.setLayoutParams(layoutParams);

        inflatedLayout.addView(newBtn);
        return counter;
    }
}