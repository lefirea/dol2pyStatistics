public class UrlEncoding{
	public static void main(String[] args) throws java.io.UnsupportedEncodingException {
		String target = args[0];
		
		String encodedResult = java.net.URLEncoder.encode(target, "UTF-8");
		System.out.print(encodedResult);
	}
}