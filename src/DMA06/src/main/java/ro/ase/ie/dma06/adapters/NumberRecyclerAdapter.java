package ro.ase.ie.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

import ro.ase.ie.dma06.R;

/**
 * Step 3: fills the same row for a RecyclerView.
 * The ViewHolder is required here, and getView is split into two methods.
 */
public class NumberRecyclerAdapter
        extends RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder> {

    static class NumberViewHolder extends RecyclerView.ViewHolder {
        final TextView tvDecimal;
        final TextView tvBinary;

        NumberViewHolder(@NonNull View itemView) {
            super(itemView);
            tvDecimal = itemView.findViewById(R.id.tvDecimal);
            tvBinary = itemView.findViewById(R.id.tvBinary);
        }
    }

    private final List<Integer> numbers;

    public NumberRecyclerAdapter(List<Integer> numbers) {
        this.numbers = numbers;
    }

    @NonNull
    @Override
    public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Runs only when a new row is needed
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_number, parent, false);
        return new NumberViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
        // Runs each time a row shows a number
        int number = numbers.get(position);
        holder.tvDecimal.setText(String.valueOf(number));
        holder.tvBinary.setText(Integer.toBinaryString(number));
    }

    @Override
    public int getItemCount() {
        return numbers.size();
    }
}
