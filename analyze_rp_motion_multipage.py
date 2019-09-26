"""Module to analyze motion parameters.

This module provides a series of functions designed to allow the evaluation
of motion parameters as output from SPM12 (i.e. rp_* files)
"""
import os
import os.path as op
import numpy as np
import math
import pickle
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from matplotlib.backends.backend_pdf import PdfPages
from operator import itemgetter


def get_user_folders():
    """Get user-entered source and results folders."""
    print("This program requires, as input, a root directory containing\n " +
          "your study subjects and a results folder where the output will\n" +
          "be stored. It is recommended that you choose a new directory\n" +
          "name, such as \"/study/results/motion_output\". If the final\n" +
          "directory does not exist, in this case \"motion_output\", it\n" +
          "will be created.\n")
    print("Note that motion parameter files are identified based on having\n" +
          "the prefix \"rp_\". The script will need to be modified if your\n" +
          "motion parameter files have a different prefix.\n")
    source_folder = input("Where are the subject folders stored? > "). \
        rstrip('/')
    results_folder = input("Where would you like to store the results? > " +
                           "").rstrip('/')
    if op.isdir(source_folder) is False:
        print("source_folder (" + source_folder + ") does not exist.")
        print("Exiting on getUserFolders()")
        return  # make sure calling functions can cope with return = None
    if op.isdir(results_folder) is False:
        if op.isdir(op.split(results_folder)[0]) is False:
            print("results_folder (" + results_folder +
                  ") and one step up do not exist.")
        else:
            print("The results folder did not exist, but the parent " +
                  "directory does. Will make the folder " + results_folder +
                  " inside " + op.split(results_folder)[0] + ".")
            os.mkdir(results_folder)
    return source_folder, results_folder


def get_default_folders():
    """For testing only: Use default source and results folders."""
    source_folder = '/data/images/exobk/'
    results_folder = '/data/images/exobk'
    return source_folder, results_folder


def get_parameter_file_list(source_folder):
    """Create a list of [directory, filename] for all rp_ files."""
    rp_file_list = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file[0:3] == 'rp_':
                rp_file_list.append([root, file])
    if len(rp_file_list) == 0:
        print("No rp_* (motion parameter) files were found " +
              "in the source directory (" + source_folder + "). " +
              "Check that the prefix is correct for your " +
              "files and that the root folder is correct.")
    else:
        print("Identified " + str(len(rp_file_list)) + " motion parameter " +
              "files in the root directory (" + source_folder + ").")
    return sorted(rp_file_list, key=itemgetter(1))


def get_motion_parameter_matrix(source, root, file):
    """Import the rp_* data and returns an Nx6 matrix.

    Keyword arguments:
    source -- Location of root directory containing all subjects
    root, file -- One element from results of getParameterFileList

    Returns:
    subject -- Subject name, derived from first-level folder name in source
    run     -- Name of the run, derived from second- and deeper folders
    rp_matrix -- Numpy matrix containing the motion parameters
    """
    source_components = source.rstrip('/').lstrip('/').split('/')
    root_components = root.rstrip('/').lstrip('/').split('/')
    full_filename = op.join(root, file)

    # Every file will need a subject name, a run name, and then a number
    # Assume that subject name is only one subfolder deep in root.
    if len(root_components) > len(source_components):
        subject = root_components[len(source_components)]
    elif len(root_components) == len(source_components):
        subject = 'root'
    else:
        print("Could not parse rp_* file structure in " +
              "in getMotionParameterMatrix. Exiting function.")
        return  # make sure calling scripts can accommodate None

    # Assume that run name is two subfolders deep in root.
    if len(root_components) > len(source_components) + 1:
        run = root_components[len(source_components)+1]
    else:
        run = 'no-run-name'

    # And if there are more than expected subfolders, just append to the run
    if len(root_components) > len(source_components) + 2:
        for elem in root_components[len(source_components)+2:]:
            run = run + '-' + elem
    rp_matrix = np.genfromtxt(full_filename)
    return subject, run, rp_matrix


def make_fd_matrix(rp_matrix, radius=50.0):
    """Calculate framewise displacement from motion parameter matrix.

    Keyword arguments:
    rp_matrix -- Numpy Nx6 matrix containing motion parameters.
    radius    -- For rotational displacement calculations. Default = 50.0 (mm)
    """
    fd_matrix = np.zeros(shape=(rp_matrix.shape[0], 7))
    for i in range(1, len(rp_matrix)):
        for j in range(0, 3):
            fd_matrix[i][j] = rp_matrix[i][j] - rp_matrix[i - 1][j]
        for j in range(3, 6):
            fd_matrix[i][j] = (rp_matrix[i][j] - rp_matrix[i - 1][j]) * radius
        fd_matrix[i][6] = sum(abs(fd_matrix[i]))
    return fd_matrix


def mean_fd(fd_matrix):
    """Return mean framewise displacement."""
    return fd_matrix.mean(axis=0)[6]


def high_fd_frames(fd_matrix, threshold=1.0):
    """Return array containing location of frames with FD > threshold."""
    return np.where(fd_matrix[:, 6] > threshold)[0]


def plot_fd(fd_matrix):
    """Simple plotting function of framewise displacements."""
    fd_col_names = ['x', 'y', 'z', 'pitch', 'roll', 'yaw', 'fd']

    plt.plot(fd_matrix)
    plt.legend(fd_col_names)
    for line in plt.gca().lines:
        line.set_linewidth(0.5)  # otherwise, hard to see everything
    plt.show()


class Motion(object):
    """A description of the motion parameters for a given subject and run.

    Stores relevant data and provides methods for analyzing the motion
    with an emphasis on framewise displacement calculations.
    """

    def __init__(self, subject, run, rp_matrix):
        """Initializer function."""
        self.subject = subject
        self.run = run
        self.rp_matrix = rp_matrix
        self.fd_matrix = make_fd_matrix(self.rp_matrix)
        self.fd_mean = mean_fd(self.fd_matrix)

    def high_fd_frames(self, threshold=0.5):
        """Return array containing location of FD>*threshold* frames."""
        return np.where(self.fd_matrix[:, 6] > threshold)[0]

    def max_rotation(self):
        """Return maximum rotational motion value for graphing."""
        maxr = 0
        for i in range(3, 6):
            high = max(abs(n) for n in self.rp_matrix[:, i])
            if high > maxr:
                maxr = high
        return maxr

    def max_translation(self):
        """Return maximum translational motion value for graphing."""
        maxt = 0
        for i in range(0, 3):
            high = max(abs(n) for n in self.rp_matrix[:, i])
            if high > maxt:
                maxt = high
        return maxt

    def plot_motion_translational(self, ax=None, show=False, maxt=2.0):
        """Return figure containing plot of x, y, and z motion."""
        if ax is None:
            ax = plt.gca()
        f = list(range(1, len(self.rp_matrix)+1))
        ax.plot(f, self.rp_matrix[:, 0:3], linewidth=0.75)
        ax.set_title('Translational Movement', fontsize=10)
        ax.legend(['x', 'y', 'z'])
        ax.set_ylabel('Movement (mm)', fontsize=8)
        ax.set_xlabel('Frames (#, in sequence)', fontsize=8)
        if(self.max_translation() < maxt):
            ax.set_ylim([-maxt, maxt])
        else:
            for axis in ['top', 'bottom', 'left', 'right']:
                ax.spines[axis].set_linewidth(1.5)
                ax.spines[axis].set_color('red')
        if show:
            plt.show()
        return ax

    def plot_motion_rotational(self, ax=None, show=False, maxr=0.05):
        """Return figure containing plot of x, y, and z motion."""
        if ax is None:
            ax = plt.gca()
        f = list(range(1, len(self.rp_matrix)+1))
        ax.plot(f, self.rp_matrix[:, 3:6], linewidth=0.75)
        ax.set_title('Rotational Movement', fontsize=10)
        ax.legend(['pitch', 'roll', 'yaw'])
        ax.set_ylabel('Rotation (rads)', fontsize=8)
        ax.set_xlabel('Frames (#, in sequence)', fontsize=8)
        if(self.max_rotation() < maxr):
            ax.set_ylim([-maxr, maxr])
        else:
            for axis in ['top', 'bottom', 'left', 'right']:
                ax.spines[axis].set_linewidth(1.5)
                ax.spines[axis].set_color('red')
        if show:
            plt.show()
        return ax

    def plot_motion(self, show=False, maxt=2.0, maxr=0.1):
        """Return figure containing two plots with all six motion params."""
        plt.style.use('seaborn-deep')
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 5))
        f.suptitle('%s [%s]: Subject Motion' % (self.subject, self.run),
                   fontsize=12, fontweight='bold')
        self.plot_motion_translational(ax1, maxt=maxt)
        self.plot_motion_rotational(ax2, maxr=maxr)
        plt.xlabel('Frames (#, in sequence)', fontsize=8)
        if show:
            plt.show()
        return f


class StudyMotion(object):
    """A list of Motion objects and methods for analyzing them as a group.

    The list of Motion objects will be garnered from the source directories
    provided by the user. Functions will examine all Motion objects as a
    whole or divided by user-selected options, such as run name.
    """

    def __init__(self, source_folder, results_folder):
        """Initalizer function."""
        self.source = source_folder
        self.results = results_folder
        self.rp_files = get_parameter_file_list(self.source)
        self.motion_list = []
        self.runs = []
        self.subjects = []
        for [root, file] in self.rp_files:
            self.motion_list.append(Motion(*get_motion_parameter_matrix(
                                    self.source, root, file)))
        for motion in self.motion_list:
            if motion.run not in self.runs:
                self.runs.append(motion.run)
            if motion.subject not in self.subjects:
                self.subjects.append(motion.subject)

    def plot_fd_by_run(self):
        """Matrix plot of all subjects' FD by run."""
        self.fd_matrix = np.empty((len(self.subjects),
                                   len(self.runs))) * np.nan
        for motion in self.motion_list:
            i = self.subjects.index(motion.subject)
            j = self.runs.index(motion.run)
            self.fd_matrix[i][j] = motion.fd_mean

        fig = plt.matshow(self.fd_matrix)
        plt.xticks(range(0, len(self.runs)), self.runs, rotation='vertical',
                   fontsize=7)
        plt.yticks(range(0, len(self.subjects)), self.subjects, fontsize=7)
        plt.xlabel('Scanning Runs')
        plt.ylabel('Subject ID')
        plt.title('Mean Framewise Displacement by Scan')
        cbar = plt.colorbar(fig)
        cbar.ax.set_ylabel('Mean Framewise Displacement')
        plt.show()
        with PdfPages(op.join(self.results,'fd_by_run.pdf')) as pdf:
            try:
                pdf.savefig(fig)
                plt.close()
            except ValueError as err:
                    print(err)

    def plot_fd_spikes_by_run(self, threshold=0.5):
        """Matrix plot showing # of spikes over *thresh* by run."""
        with PdfPages(op.join(self.results,'fd_spikes.pdf')) as pdf:
            subjs_on_page = 40
            page_num = int(round(len(self.subjects)/subjs_on_page,0))
            self.fig = ['']*page_num
            self.fig_name = ['page_'+ str(x+1) for x in range(page_num)]
            for p,name in enumerate(self.fig_name):
                plt.title('Frames with FD > {} by Scan - Page {}'.format(threshold,name))
                plt.xlabel('Scanning Runs')
                plt.ylabel('Subject ID')

                spike_matrix = np.empty((subjs_on_page,
                                          len(self.runs))) * np.nan
                for motion in self.motion_list[p*subjs_on_page:(p+1)*subjs_on_page]:
                    i = self.subjects.index(motion.subject)
                    j = self.runs.index(motion.run)
                    spike_matrix[i][j] = len(motion.high_fd_frames(
                                                  threshold=threshold))
                self.fig[p] = plt.matshow(spike_matrix)
                plt.xticks(range(0, len(self.runs)), self.runs,
                           rotation='vertical', fontsize=7)
                plt.yticks(range(0, subjs_on_page), self.subjects[p*subjs_on_page:(p+1)*subjs_on_page], fontsize=7)
                cbar = plt.colorbar(self.fig[p])
                cbar.ax.set_ylabel('# of Frames Meeting FD > {}'.format(threshold))
                plt.show()
                try:
                    pdf.savefig()
                except ValueError:
                    print('Figure not evaluated')
                plt.close()

        pkl_file = op.join(self.results,'fd_spikes_fig.txt')
        with open(pkl_file, 'wb') as file:
            pickle.dump(self.fd_fig, file)

    def plot_motion_for_subject(self, subject, runs=None, show=True):
        """Plot motion graphs of all runs for a given subject."""
        subject_runs = []
        for motion in self.motion_list:
            if motion.subject == subject:
                if not runs:
                    subject_runs.append(motion)
                elif motion.run in runs:
                    subject_runs.append(motion)
        if len(subject_runs) == 0:
            raise ValueError('No runs found for subject: %s', subject)
        fig = plt.figure(figsize=(8, 11))
        fig.suptitle('%s: Subject Motion' % (subject),
                     fontsize=12, fontweight='bold')
        outer = gs.GridSpec(int(math.ceil(len(subject_runs)/2)), 2,
                            wspace=0.2, hspace=0.3)
        for i in range(len(subject_runs)):
            inner = gs.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[i],
                                               wspace=0.1, hspace=0.1)
            for j in range(2):
                ax = plt.Subplot(fig, inner[j])
                if j == 0:
                    subject_runs[i].plot_motion_translational(ax=ax)
                    ax.set_xticks([])
                    ax.set_title('%s [%s]' % (subject, subject_runs[i].run),
                                 fontsize='small')
                if j == 1:
                    subject_runs[i].plot_motion_rotational(ax=ax)
                    ax.set_title('')
                # The following is added to remove some of the formatting
                ax.legend_.remove()
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.tick_params('both', labelsize='x-small')
                fig.add_subplot(ax)
        if show:
            fig.show()
        else:
            return fig

    def make_motion_report(self, filename='motion_report'):
        """Produce motion graphs of all runs and print into filename as pdf."""
        with PdfPages(op.join(self.results,(filename + '.pdf'))) as pdf:
            for subject in self.subjects:
                try:
                    fig = self.plot_motion_for_subject(subject, show=False)
                    pdf.savefig(fig)
                    plt.close()
                except ValueError as err:
                    print(err)

if __name__ == "__main__":
    #[src, res] = get_user_folders()
    [src, res] = get_default_folders()
    print('Loading. Please wait.\n')
    rpt = StudyMotion(src,res)
    #rpt.plot_fd_by_run()
    #rpt.plot_fd_spikes_by_run()
    subjs = glob.glob(os.path.join(src,'exo20*','fp_run?'))
    with PdfPages(op.join(src,('rps.pdf'))) as pdf:
        for subj in subjs:
            try:
                fig = rpt.plot_motion_for_subject(subj, show=False)
                print('processing ' + subj)
                fig.show()
                pdf.savefig(fig)
                fig.close()
            except ValueError as e:
                print(e)
                pass
    rpt.make_motion_report()
