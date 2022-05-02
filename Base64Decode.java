import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.util.Base64;
import java.io.*;

public class Base64Decode{
	public static void main(String[] args){
		String source = args[0];
		
		byte[] bytes = Base64.getDecoder().decode(source);
		
		File file = new File("./result.png");
		try{
			file.createNewFile();
		}catch(IOException ioe){
			//pass
		}
		
		try{
			FileOutputStream fos = new FileOutputStream(file);
			fos.write(bytes);
			fos.flush();
			fos.close();
		}catch(FileNotFoundException e){
			//pass;
		}catch(IOException e){
			//pass;
		}
	}
}
