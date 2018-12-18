/***
 * Simple command line tool to do AWSMultiPartUpload. Useful for uploading Virtual disk images for AMI creations when are working in a restricted environment
 ***/
package aws.tools;

import java.io.File;

import com.amazonaws.AmazonClientException;
import com.amazonaws.event.ProgressEvent;
import com.amazonaws.event.ProgressListener;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.amazonaws.services.s3.transfer.TransferManager;
import com.amazonaws.services.s3.transfer.TransferManagerBuilder;
import com.amazonaws.services.s3.transfer.Upload;

/**
 * @author Vijay Reddiar
 *
 */
public class AWSMultiPartUploadCmd {

	public static void main(String[] args) {
		if (args.length != 3) {
			System.out.println("Usage:");
			System.out.println("java -jar AWSMultiPartUpload.jar <existingBucketName> <keyName> <filePath>");
			System.exit(1);
		}
		String existingBucketName = args[0];
		String keyName = args[1];
		String filePath = args[2];
		System.out.println("Using following parameter:");
		System.out.println("\texistingBucketName = " + existingBucketName);
		System.out.println("\tkeyName = " + keyName);
		System.out.println("\tfilePath = " + filePath);
		
		TransferManager tm = TransferManagerBuilder.defaultTransferManager();

		ProgressListener progressListener = new ProgressListener() {

			public void progressChanged(ProgressEvent progressEvent) {
				System.out.print(progressEvent.getBytesTransferred() + " ");
			}
		};
		
		File uploadFile = new File(filePath);
		PutObjectRequest request = new PutObjectRequest(
				existingBucketName, keyName, uploadFile).withGeneralProgressListener(progressListener);

		Upload upload = tm.upload(request);
		System.out.print("Transferred bytes: ");
        try {
        	//block and wait for the upload to finish
        	upload.waitForCompletion();
        	System.out.println("\nSuccessfully Uploaded file " + uploadFile.getName() + " of size, " 
        			+ uploadFile.length() + " bytes");
        } catch (AmazonClientException amazonClientException) {
        	System.out.println("Unable to upload file, upload aborted.");
        	amazonClientException.printStackTrace();
        } catch (InterruptedException e) {
			e.printStackTrace();
		}
        System.exit(0);
	}

}
