package createresources;

import java.sql.*;
import java.util.LinkedList;

public class SqliteConnection {

    public static Connection connectSqlite(
            String sqlitePath
    ) throws SQLException {
        if (sqlitePath == null) sqlitePath = "../legacydb.sqlite3"; // TODO: 06/05/22 change the path?
        String connectionString = String.format("jdbc:sqlite:%s", sqlitePath);
        Connection conn = null;
        conn = DriverManager.getConnection(connectionString);
        return conn;
    }

    public static LinkedList<LaboratoryCodeConcept> selectAll(String sqlitePath) {
        String sql = "SELECT code, display, unit, loinc FROM lab_codes;";
        try (Connection conn = connectSqlite(sqlitePath);
             ResultSet rs = conn.createStatement().executeQuery(sql)
        ) {
            LinkedList<LaboratoryCodeConcept> laboratoryCodeConcepts = new LinkedList<>();
            while (rs.next()) {
                laboratoryCodeConcepts.add(
                        new LaboratoryCodeConcept(
                                rs.getString("code"),
                                rs.getString("display"),
                                rs.getString("unit"),
                                rs.getString("loinc")));
            }
            return laboratoryCodeConcepts;
        } catch (SQLException e) {
            e.printStackTrace();
            System.exit(1);
        }
        return null;
    }

}



