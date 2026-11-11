package ro.ase.ie.dma06.activities;

import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.data.NumberData;
import ro.ase.ie.dma06.R;


/**
 * Step 1: one column.
 * ArrayAdapter is enough because each row shows one text value.
 */
public class SingleColumnActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_single_column);

        ListView lvNumbers = findViewById(R.id.lvNumbers);

        // ArrayAdapter calls toString() on each number and shows it in a TextView
        ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
                this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
        lvNumbers.setAdapter(adapter);
    }
}
