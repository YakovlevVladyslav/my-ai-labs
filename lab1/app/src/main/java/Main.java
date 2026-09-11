import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // (abc)ⁿ(bcd)ᵐe, n ≥ 0, m ≥ 0, n + m ≥ 1
        String regex = "^(?:(abc)+(bcd)*|(abc)*(bcd)+)e$";

        System.out.print("Enter string: ");
        String input = scanner.nextLine();

        if (input.matches(regex)) {
            System.out.println("The string matches the pattern.");
        } else {
            System.out.println("The string does not match the pattern.");
        }

        scanner.close();
    }
}