package VASSAL.launch;

import VASSAL.build.GameModule;
import VASSAL.build.module.metadata.ModuleMetaData;
import VASSAL.tools.DataArchive;
import VASSAL.tools.SequenceEncoder;
import VASSAL.tools.io.*;

import java.awt.event.KeyEvent;
import java.io.*;
import java.util.HashMap;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;


/**
 * Created with IntelliJ IDEA.
 * User: lhayhurst
 * Date: 5/28/14
 * Time: 8:28 AM
 * To change this template use File | Settings | File Templates.
 */


public class VlogCutter {

    public static final String SAVEFILE_ZIP_ENTRY = "savedGame";  //$NON-NLS-1$
    public static final String LOG_CHAT = "LOG\tCHAT";
    public static final String LOG_ADD = "LOG\t+";
    public static final String LOG_ADD_COMMAND_SEPARATOR = "LOG\t+/";
    public static final String ALTERED_COURSE_ON_A_MOVEMENT_DIAL = "altered course on a Movement Dial";
    public static final String LOG_D = "LOG\tD";
    private static char COMMAND_SEPARATOR = (char) KeyEvent.VK_ESCAPE;
    private static final char PARAM_SEPARATOR = '/';
    public static final String ADD = "+" + PARAM_SEPARATOR;

    private java.util.HashMap<String, String> dials = new HashMap<String, String>();
    private java.util.HashMap<String, String> dialsIds = new HashMap<String, String>();

    public static String MODULE;
    private SequenceEncoder sequenceEncoder = new SequenceEncoder(COMMAND_SEPARATOR);
    private DataArchive sourceArchive;
    private boolean stripChatRecords = false;

    public VlogCutter(DataArchive archive, boolean stripChatRecords) {
        this.stripChatRecords = stripChatRecords;
        this.sourceArchive = archive;
        dialsIds.put("1597", "Z95");
        dialsIds.put("844", "YT-1300");
        dialsIds.put("776", "Y-Wing");
        dialsIds.put("450", "X-Wing");
        dialsIds.put("1387", "HWK");
        dialsIds.put("845", "B-Wing");
        dialsIds.put("777", "A-Wing");
        dialsIds.put("850", "Firespray-1300");
        dialsIds.put("862", "Lambda");
        dialsIds.put("847", "Tie Adv");
        dialsIds.put("851", "Tie Bomber");
        dialsIds.put("451", "Tie Fighter");
        dialsIds.put("849", "Tie Interceptor");
        dialsIds.put("1694", "Tie Phantom");

    }


    public void decodeSavedGame(InputStream in, String saveFile) throws IOException {

        //first shove all the contents of the file into a single string.  it's the vassal way!
        ZipInputStream zipInput = new ZipInputStream(in);
        String command = null;
        for (ZipEntry entry = zipInput.getNextEntry(); entry != null;
             entry = zipInput.getNextEntry()) {
            if (SAVEFILE_ZIP_ENTRY.equals(entry.getName())) {
                DeobfuscatingInputStream din = null;

                din = new DeobfuscatingInputStream(zipInput);
                command = IOUtils.toString(din, "UTF-8");
                din.close();
                break;
            }
        }
        zipInput.close();

        //decode it
        decode(command);

        //and save it
        File output = new File(saveFile);
        final String save = sequenceEncoder.getValue();
        final FastByteArrayOutputStream ba = new FastByteArrayOutputStream();
        OutputStream out = null;
        try {
            out = new ObfuscatingOutputStream(ba);
            out.write(save.getBytes("UTF-8"));
            out.close();
        } finally {
            IOUtils.closeQuietly(out);
        }

        //add the X-Wing module to the saved game
        FileArchive archive = null;
        try {
            archive = new ZipArchive(output);
            archive.add(SAVEFILE_ZIP_ENTRY, ba.toInputStream());

            //copied over from SaveMetaData
            try {
                BufferedInputStream bis = new BufferedInputStream(this.sourceArchive.getInputStream(ModuleMetaData.ZIP_ENTRY_NAME));
                archive.add(ModuleMetaData.ZIP_ENTRY_NAME, bis);
                bis.close();
            } catch (FileNotFoundException e) {
                // No Metatdata in source module, create a fresh copy
                new ModuleMetaData(GameModule.getGameModule()).save(archive);
            } finally {
                IOUtils.closeQuietly(in);
            }

            archive.close();
        } finally {
            IOUtils.closeQuietly(archive);
        }
    }


    private String unwrapNull(String s) {
        return "null".equals(s) ? null : s; //$NON-NLS-1$
    }

    void decode(String command) {
        int numStripped = 0;
        int numRead = 0;
        if (command == null) {
            return;
        }

        final SequenceEncoder.Decoder st =
                new SequenceEncoder.Decoder(command, COMMAND_SEPARATOR);

        while (st.hasMoreTokens()) {
            numRead++;
            String tok = st.nextToken();
            //System.out.println(tok);

            if (stripChatRecords) {
                if (tok.startsWith(LOG_CHAT)) {
                    numStripped++;
                    continue;
                }
            }

            if (tok.startsWith(LOG_ADD)) {
                sequenceEncoder.append(tok);
                String subcommand = tok.substring(LOG_ADD_COMMAND_SEPARATOR.length());
                SequenceEncoder.Decoder std = new SequenceEncoder.Decoder(subcommand, PARAM_SEPARATOR);
                String id = unwrapNull(std.nextToken());
                String type = std.nextToken();
                if (type.contains(ALTERED_COURSE_ON_A_MOVEMENT_DIAL)) {
                    dials.put(id, id);
                }
            } else {
                boolean skipToken = false;
                if (tok.startsWith(LOG_D)) {

                    for (String key : dials.keySet()) {
                        if (tok.contains(key)) {
                            skipToken = true;
                        }
                    }
                    if (skipToken == false) {
                        //keep trying.  now see if the log record ends with a dial id
                        for (String dialID : dialsIds.keySet()) {
                            if (tok.endsWith(dialID)) {
                                skipToken = true;
                                break;
                            }
                        }
                    }
                }
                if (!skipToken) {
                    sequenceEncoder.append(tok);
                } else {
                    numStripped++;
                }
            }

        }
        System.out.println("Stripped out " + numStripped + " records out of " + numRead);
    }


    public static void main(String args[]) throws IOException, LaunchRequestException {
        String mod = args[0];
        DataArchive archive = new DataArchive(new File(mod).getPath());
        File vlog = new File(args[1]);
        String saveFile = args[2];
        VlogCutter v = new VlogCutter(archive, true);
        VlogCutter.MODULE = mod;
        v.decodeSavedGame(new BufferedInputStream(new FileInputStream(vlog)), saveFile);

    }

}
