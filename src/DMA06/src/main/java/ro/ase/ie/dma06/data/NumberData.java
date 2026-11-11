package ro.ase.ie.data;

import java.util.ArrayList;
import java.util.List;

/** The data source shared by all three steps. */
public final class NumberData {

    private static final int FIRST_NUMBER = 1;
    private static final int LAST_NUMBER = 100;

    private NumberData() {
        // This class only has static methods
    }

    public static List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();
        for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {
            numbers.add(number);
        }
        return numbers;
    }
}
